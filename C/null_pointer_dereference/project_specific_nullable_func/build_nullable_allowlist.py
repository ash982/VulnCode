#!/usr/bin/env python3
"""
build_nullable_allowlist.py

Step 1: Discovers all nullable pointer-returning functions in a C/C++ codebase
        by running find_nullable_functions.yaml and parsing the semgrep JSON output.

Step 2: Generates a precise semgrep rules file (null_ptr_generated.yaml) that
        uses an exact function-name allowlist instead of a heuristic regex.

        Five rules are generated:
          Rule 1 — Discarded return value           (replaces: discarded-pointer-function-return)
          Rule 2 — Assigned pointer, no NULL check  (replaces: unchecked-pointer-before-use)
          Rule 3 — Struct member access unchecked   (replaces: unchecked-struct-member-access)
          Rule 4 — Chained call, inner unchecked    (replaces: unchecked-chained-call-result)
                   $OUTER is constrained to exclude null-safe functions discovered by
                   find-null-safe-functions (panw.c.general.find-null-safe-functions.yaml)
          Rule 5 — Taint: NULL propagation          (replaces: null-pointer-unchecked-taint)

        Rules 1–4 fully replace their heuristic counterparts. Do NOT run both.
        Rule 5 replaces null-pointer-unchecked-taint. Do NOT run both.

Usage:
    # Run all discovery rules and pipe combined output into this script
    semgrep --config panw.c.general.find-nullable-functions.yaml \
            --config panw.c.general.find-null-safe-functions.yaml \
            --config panw.c.general.find-nonnull-annotated-functions.yaml \
            --json <src_dir> \
        | python build_nullable_allowlist.py [--output null_ptr_generated.yaml]

    # Or point at an existing semgrep JSON result file
    python build_nullable_allowlist.py --input semgrep_results.json \
                                       --output null_ptr_generated.yaml

    # Dry-run: just print the discovered function lists
    python build_nullable_allowlist.py --input semgrep_results.json --list-only
"""

import argparse
import json
import sys
from pathlib import Path

# ── Rule IDs from find_nullable_functions.yaml ────────────────────────────────
NULLABLE_RULE_IDS = {
    "find-nullable-functions",
    "find-nullable-functions-nullptr",
}
NONNULL_RULE_IDS = {
    "find-nonnull-annotated-functions",
}
NULL_SAFE_RULE_IDS = {
    "find-null-safe-functions",
}

METAVAR_FUNC = "FUNC"

# ── Fixed stdlib functions always included as taint sources (Rule 5) ──────────
# These return NULL on failure but are not discoverable via find_nullable_functions
# (source not in the scanned codebase). Combined with project-specific functions
# in Rule 5 to replace the heuristic regex in null-pointer-unchecked-taint.
STDLIB_NULLABLE_FUNCS: set[str] = {
    "malloc", "calloc", "strdup", "strndup",
    "getenv", "fopen", "fdopen", "freopen", "opendir", "dlopen", "popen",
    "strstr", "strchr", "strrchr", "strpbrk", "memmem",
}

# ── Known third-party nullable functions (Rules 4 and 5) ──────────────────────
# Functions from third-party libraries whose source is not available for scanning
# by find_nullable_functions. Add entries here when a library function is known
# to return NULL on failure and is used in chained calls or assigned without check.
# Format: "function_name",  # library — return-NULL condition
KNOWN_THIRD_PARTY_NULLABLE: set[str] = {
    # OpenSSL — X509
    "X509_get_issuer_name",       # OpenSSL — returns NULL if cert has no issuer
    "X509_get_subject_name",      # OpenSSL — returns NULL if cert has no subject
    "X509_get_pubkey",            # OpenSSL — returns NULL on failure
    # OpenSSL — BIO
    "BIO_new",                    # OpenSSL — returns NULL on allocation failure
    "BIO_new_mem_buf",            # OpenSSL — returns NULL on failure
    # OpenSSL — EVP
    "EVP_get_digestbyname",       # OpenSSL — returns NULL if digest not found
    "EVP_MD_CTX_new",             # OpenSSL — returns NULL on allocation failure
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", "-i", default="-",
                   help="Semgrep JSON output file (default: stdin)")
    p.add_argument("--output", "-o", default="null_ptr_generated.yaml",
                   help="Generated semgrep rules output file (default: null_ptr_generated.yaml)")
    p.add_argument("--list-only", action="store_true",
                   help="Print discovered function names and exit without writing rules")
    p.add_argument("--min-occurrences", type=int, default=1,
                   help="Minimum number of return-NULL sites for a function to be included (default: 1)")
    return p.parse_args()


def load_semgrep_json(source: str) -> dict:
    if source == "-":
        data = sys.stdin.read()
    else:
        data = Path(source).read_text()
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: Failed to parse semgrep JSON output: {e}")


def extract_functions(results: dict, min_occurrences: int) -> tuple[set[str], set[str], set[str]]:
    """
    Returns (nullable_funcs, nonnull_funcs, null_safe_funcs) extracted from semgrep findings.
    nullable_funcs:   functions with at least one return-NULL path → taint sources / $INNER
    nonnull_funcs:    functions annotated returns_nonnull → excluded from nullable list
    null_safe_funcs:  functions that check pointer params for NULL → excluded from $OUTER in Rule 4
    """
    nullable_counts: dict[str, int] = {}
    nonnull_funcs: set[str] = set()
    null_safe_funcs: set[str] = set()

    for finding in results.get("results", []):
        rule_id = finding.get("check_id", "").split(".")[-1]  # strip rule file prefix
        metavars = finding.get("extra", {}).get("metavars", {})
        func_name = metavars.get(f"${METAVAR_FUNC}", {}).get("abstract_content", "")
        # Semgrep represents "Class::Method" as "Class Method" in abstract_content — restore "::"
        if " " in func_name:
            func_name = func_name.replace(" ", "::", 1)

        if not func_name:
            continue

        if rule_id in NULLABLE_RULE_IDS:
            nullable_counts[func_name] = nullable_counts.get(func_name, 0) + 1
        elif rule_id in NONNULL_RULE_IDS:
            nonnull_funcs.add(func_name)
        elif rule_id in NULL_SAFE_RULE_IDS:
            null_safe_funcs.add(func_name)

    nullable_funcs = {f for f, count in nullable_counts.items() if count >= min_occurrences}
    # Remove any function that is also annotated nonnull (annotation wins)
    nullable_funcs -= nonnull_funcs

    return nullable_funcs, nonnull_funcs, null_safe_funcs


def build_exact_regex(func_names: set[str]) -> str:
    """Build a semgrep metavariable-regex that exactly matches the given function names."""
    escaped = sorted(func_names)
    return "^(" + "|".join(escaped) + ")$"


def generate_rules(nullable_funcs: set[str], nonnull_funcs: set[str], null_safe_funcs: set[str]) -> str:
    """Generate a semgrep YAML rules file with exact function allowlist."""
    if not nullable_funcs and not KNOWN_THIRD_PARTY_NULLABLE:
        sys.exit("No nullable functions found. Nothing to generate.")

    # All patterns match call sites where $FUNC/$INNER/$OUTER is an unqualified name.
    # Strip "Class::" prefix from definition-discovered names before building regexes.
    nullable_unqualified = {name.split("::")[-1] for name in nullable_funcs}

    # Rules 1–4 ($FUNC/$INNER): project + known third-party nullable
    # Catches chained calls like X509_NAME_oneline(X509_get_issuer_name(...))
    inner_funcs = nullable_unqualified | KNOWN_THIRD_PARTY_NULLABLE
    exact_regex = build_exact_regex(inner_funcs)
    # Rule 5: project + stdlib + known third-party nullable
    taint_funcs = nullable_unqualified | STDLIB_NULLABLE_FUNCS | KNOWN_THIRD_PARTY_NULLABLE
    taint_regex = build_exact_regex(taint_funcs)

    func_list_comment = "\n    #   - ".join(sorted(nullable_funcs)) or "(none discovered)"
    stdlib_list_comment = ", ".join(sorted(STDLIB_NULLABLE_FUNCS))
    third_party_list_comment = ", ".join(sorted(KNOWN_THIRD_PARTY_NULLABLE))

    # Rule 4: build $OUTER exclusion regex from null-safe functions if any were discovered.
    # "Flag when a nullable inner result goes directly into an outer function... unless that outer function is known to be null-safe."    
    # $OUTER matches the unqualified callee name at a call site, so strip any "Class::" prefix.
    # One side effect to be aware of: if two different classes have a method with the same name but only one is null-safe, stripping the class prefix will incorrectly suppress Rule 4 for 
    # the other class too. For example, GetHttpResponse appears on four classes — if any one of them is null-safe, all four get excluded. That's a conservative trade-off (fewer false
    # positives, possible false negatives)
    if null_safe_funcs:
        null_safe_unqualified = {name.split("::")[-1] for name in null_safe_funcs}
        null_safe_list = "|".join(sorted(null_safe_unqualified))
        outer_constraint = f"""\
      - metavariable-regex:
          metavariable: $OUTER
          regex: '^(?!({null_safe_list})$).*'"""
        null_safe_comment = f"# Null-safe functions excluded from $OUTER ({len(null_safe_funcs)}): " + ", ".join(sorted(null_safe_funcs))
    else:
        outer_constraint = ""
        null_safe_comment = "# No null-safe functions discovered — $OUTER is unconstrained"

    rules = f"""\
# AUTO-GENERATED by build_nullable_allowlist.py
# DO NOT EDIT MANUALLY — re-run the script to refresh after code changes.
#
# Nullable functions discovered ({len(nullable_funcs)}):
#   - {func_list_comment}
#
# Non-null annotated functions excluded ({len(nonnull_funcs)}):
#   - {", ".join(sorted(nonnull_funcs)) or "(none)"}
#
# Fixed stdlib nullable functions (always included in Rule 5 taint sources):
#   {stdlib_list_comment}
#
# Known third-party nullable functions (included in Rule 4 $INNER + Rule 5 taint sources):
#   {third_party_list_comment}
#
# {null_safe_comment}
#
# Rules 1-4 replace their heuristic counterparts — do NOT run both.
# Rule 5 replaces null-pointer-unchecked-taint — do NOT run both.

rules:
  # ── Rule 1: Discarded return value ──────────────────────────────────────────
  # Replaces: discarded-pointer-function-return
  - id: generated-discarded-nullable-return
    message: >
      Return value of `$FUNC()` is discarded. This function can return NULL;
      callers must check the result before using any output buffers.
    severity: WARNING
    languages: [c, cpp]
    metadata:
      cwe: CWE-252
      generated: true
    patterns:
      - pattern: $FUNC(...);
      - pattern-not: $VAR = $FUNC(...);
      - pattern-not: return $FUNC(...);
      - pattern-not: if ($FUNC(...)) {{ ... }}
      - pattern-not: if (!$FUNC(...)) {{ ... }}
      - pattern-not: if ($FUNC(...) == NULL) {{ ... }}
      - pattern-not: if ($FUNC(...) != NULL) {{ ... }}
      - metavariable-regex:
          metavariable: $FUNC
          regex: '{exact_regex}'

  # ── Rule 2: Assigned pointer used without NULL check ────────────────────────
  # Replaces: unchecked-pointer-before-use
  - id: generated-unchecked-nullable-pointer-use
    message: >
      Pointer `$PTR` returned by `$FUNC()` is used without a NULL check.
      This function can return NULL; dereferencing it causes undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
      generated: true
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $SINK($PTR, ...);
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR != NULL) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          assert($PTR);
      - metavariable-regex:
          metavariable: $FUNC
          regex: '{exact_regex}'

  # ── Rule 3: Struct member access on unchecked pointer ───────────────────────
  # Replaces: unchecked-struct-member-access
  - id: generated-unchecked-struct-member-access
    message: >
      Pointer `$PTR` from `$FUNC()` is used to access `$FIELD` without a NULL check.
      This function can return NULL; the member access will crash.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
      generated: true
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $PTR->$FIELD;
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) {{ ... }}
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) {{ ... }}
      - metavariable-regex:
          metavariable: $FUNC
          regex: '{exact_regex}'

  # ── Rule 4: Chained call — inner result passed without NULL check ────────────
  # Replaces: unchecked-chained-call-result
  # $INNER constrained to known nullable functions (exact list).
  # $OUTER constrained to exclude known null-safe functions (discovered by find-null-safe-functions).
  - id: generated-unchecked-chained-nullable-call
    message: >
      Return value of `$INNER()` is passed directly to `$OUTER()` without a NULL check.
      `$INNER()` can return NULL; passing it unchecked causes undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
      generated: true
    patterns:
      - pattern: $OUTER($INNER(...), ...)
      - metavariable-regex:
          metavariable: $INNER
          regex: '{exact_regex}'
{outer_constraint}

  # ── Rule 5: Taint — NULL propagation (intra and cross-file) ─────────────────
  # Replaces: null-pointer-unchecked-taint
  # Sources: exact project nullable functions + fixed stdlib nullable functions.
  # This eliminates the heuristic regex overfitting of the original rule.
  - id: generated-null-pointer-unchecked-taint
    mode: taint
    message: >
      Value from `$SOURCE` flows into `$SINK` without a NULL check.
      The source function can return NULL; using it unchecked causes undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    options:
      interfile: true   # required — tracks NULL across file boundaries (patterns 2 inter, 10)
    metadata:
      cwe: [CWE-476, CWE-690]
      generated: true
    pattern-sources:
      - patterns:
          - pattern: $FUNC(...)
          - metavariable-regex:
              metavariable: $FUNC
              regex: '{taint_regex}'
    pattern-sanitizers:
      - pattern: if (!$X) {{ ... }}
      - pattern: if ($X == NULL) {{ ... }}
      - pattern: if ($X != NULL) {{ ... }}
      - pattern: if ($X) {{ ... }}
      - pattern: assert($X)
    pattern-sinks:
      - patterns:
          - pattern: $FUNC($X, ...)
          - metavariable-regex:
              metavariable: $FUNC
              regex: (?i).*(print|strstr|strcmp|strlen|memcpy|strchr|fread|fwrite).*
"""
    return rules


def main() -> None:
    args = parse_args()

    raw = load_semgrep_json(args.input)
    nullable_funcs, nonnull_funcs, null_safe_funcs = extract_functions(raw, args.min_occurrences)

    print(f"[+] Nullable functions found:       {len(nullable_funcs)}", file=sys.stderr)
    print(f"[+] Non-null annotated (excluded):  {len(nonnull_funcs)}", file=sys.stderr)
    print(f"[+] Null-safe functions (excluded from $OUTER): {len(null_safe_funcs)}", file=sys.stderr)
    print(f"[+] Known third-party nullable (seeded): {len(KNOWN_THIRD_PARTY_NULLABLE)}", file=sys.stderr)

    if args.list_only:
        print("\nNullable functions (project-discovered):")
        for f in sorted(nullable_funcs):
            print(f"  {f}")
        if nonnull_funcs:
            print("\nExcluded (returns_nonnull annotated):")
            for f in sorted(nonnull_funcs):
                print(f"  {f}")
        if null_safe_funcs:
            print("\nNull-safe functions (excluded from $OUTER in Rule 4):")
            for f in sorted(null_safe_funcs):
                print(f"  {f}")
        print("\nKnown third-party nullable functions (Rule 4 $INNER + Rule 5 taint sources):")
        for f in sorted(KNOWN_THIRD_PARTY_NULLABLE):
            print(f"  {f}")
        print("\nFixed stdlib nullable functions (Rule 5 taint sources):")
        for f in sorted(STDLIB_NULLABLE_FUNCS):
            print(f"  {f}")
        return

    rules_yaml = generate_rules(nullable_funcs, nonnull_funcs, null_safe_funcs)
    Path(args.output).write_text(rules_yaml)
    print(f"[+] Generated rules written to: {args.output}", file=sys.stderr)
    print(f"[+] Rules 1-4 replace heuristic OSS rules — do not run both.", file=sys.stderr)
    print(f"[+] Rule 5 replaces null-pointer-unchecked-taint — do not run both.", file=sys.stderr)
    print(f"[+] Run: semgrep --pro --config {args.output} <src_dir>", file=sys.stderr)


if __name__ == "__main__":
    main()
