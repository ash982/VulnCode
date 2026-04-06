# Null Pointer Dereference (CWE-476)

## Overview

A null pointer dereference occurs when a program attempts to use a pointer that has not been assigned a valid memory address (i.e., is `NULL`). This results in undefined behavior, typically a crash (segmentation fault), and can be exploited to cause denial of service or, in rare cases, arbitrary code execution.

---

## Vulnerability Patterns

### Pattern 1: Unchecked Return Value (Discarded)

The return value of a function that can return `NULL` is completely ignored.

```c
// VULNERABLE
X509_NAME_oneline(issuer, buf, 1024);  // returns NULL on failure
strstr(buf, "/CN=");                   // buf may be uninitialized
```

```c
// SAFE
if (X509_NAME_oneline(issuer, buf, sizeof(buf)) == NULL) {
    handle_error();
    return;
}
strstr(buf, "/CN=");
```

---

### Pattern 2: Assigned Pointer Used Without NULL Check

A pointer is assigned from a function return value and used without verifying it is non-NULL.

```c
// VULNERABLE
X509_NAME *issuer = X509_get_issuer_name(ccert);
X509_NAME_oneline(issuer, buf, 1024);  // crash if issuer == NULL
```

```c
// SAFE
X509_NAME *issuer = X509_get_issuer_name(ccert);
if (issuer == NULL) {
    handle_error();
    return;
}
X509_NAME_oneline(issuer, buf, 1024);
```

---

### Pattern 3: Chained Call Without NULL Check

The return value of an inner function is passed directly to an outer function without an intermediate NULL check.

```c
// VULNERABLE
X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024);
//                ^^^^^^^^^^^^^^^^^^^^^^^^^^ can return NULL
```

```c
// SAFE
X509_NAME *name = X509_get_issuer_name(ccert);
if (name == NULL) {
    handle_error();
    return;
}
X509_NAME_oneline(name, buf, sizeof(buf));
```

---

### Pattern 4: Pointer Parameter Dereferenced Without NULL Check

A function accepts a pointer parameter and dereferences it without first validating it is non-NULL.

```c
// VULNERABLE
size_t OPENSSL_strnlen(const char *str, size_t maxlen)
{
    const char *p;
    for (p = str; maxlen-- != 0 && *p != '\0'; ++p) ;
    //                                  ^^ NULL deref if str == NULL
    return p - str;
}
```

```c
// SAFE
size_t OPENSSL_strnlen(const char *str, size_t maxlen)
{
    const char *p;
    if (str == NULL)
        return 0;
    for (p = str; maxlen-- != 0 && *p != '\0'; ++p) ;
    return p - str;
}
```

#### Indirect Dereference Variant

NULL dereference through an intermediate pointer copy is harder to detect statically:

```c
// VULNERABLE — dereference is indirect via p = str
const char *p = str;   // p inherits NULL from str
*p;                    // NULL deref — tools may miss this
```

---

### Pattern 5: Failed Memory Allocation

`malloc`, `calloc`, and `realloc` return `NULL` on failure. Using the result without checking causes a crash.

```c
// VULNERABLE
char *buf = malloc(1024);
strcpy(buf, input);     // crash if malloc returned NULL
```

```c
// VULNERABLE — realloc failure leaks original pointer
buf = realloc(buf, new_size);   // if realloc fails: returns NULL AND buf is now lost
memcpy(buf, src, new_size);     // crash + memory leak
```

```c
// SAFE
char *buf = malloc(1024);
if (buf == NULL) { handle_error(); return; }

// SAFE — realloc pattern
char *tmp = realloc(buf, new_size);
if (tmp == NULL) { free(buf); handle_error(); return; }
buf = tmp;
```

---

### Pattern 6: Unchecked Struct Member Access

A pointer to a struct is used to access members without checking if the pointer is NULL.

```c
// VULNERABLE
struct Node *node = find_node(list, key);
node->value = 42;           // crash if find_node returned NULL
printf("%s", node->name);
```

```c
// SAFE
struct Node *node = find_node(list, key);
if (node == NULL) { handle_error(); return; }
node->value = 42;
```

---

### Pattern 7: String Search Functions Returning NULL

`strstr`, `strchr`, `strtok`, etc. return `NULL` when the search fails. Using the result without checking causes a crash or pointer arithmetic UB.

```c
// VULNERABLE
char *p = strstr(buf, "key=");
p += 4;                     // crash if "key=" not found — p is NULL
printf("%s", p);
```

```c
// VULNERABLE — pointer arithmetic on NULL
char *end = strchr(str, '/');
size_t len = end - str;     // UB if '/' not found
```

```c
// SAFE
char *p = strstr(buf, "key=");
if (p == NULL) { handle_error(); return; }
p += 4;
```

---

### Pattern 8: Environment and System Functions

`getenv`, `fopen`, `opendir`, `dlopen`, etc. return `NULL` when the resource does not exist.

```c
// VULNERABLE
char *home = getenv("HOME");
strlen(home);               // crash if HOME is not set

FILE *f = fopen("config.txt", "r");
fread(buf, 1, 100, f);      // crash if file does not exist
```

```c
// SAFE
char *home = getenv("HOME");
if (home == NULL) { handle_error(); return; }

FILE *f = fopen("config.txt", "r");
if (f == NULL) { handle_error(); return; }
```

---

### Pattern 9: Conditional NULL (Only Set in Some Code Paths)

A pointer is initialized to `NULL` and only assigned in certain branches, but used unconditionally afterwards.

```c
// VULNERABLE
char *result = NULL;
if (condition) {
    result = allocate();
}
process(result);            // crash when condition is false
```

```c
// SAFE
char *result = NULL;
if (condition) {
    result = allocate();
}
if (result == NULL) { handle_error(); return; }
process(result);
```

---

### Pattern 10: NULL Propagation

A function returns the result of an inner function call that may be `NULL`, and the caller does not check before using it.

```c
// VULNERABLE
char *get_cn(X509 *cert) {
    return strdup(X509_get_subject_name(cert));
    // X509_get_subject_name may return NULL — strdup(NULL) is UB
}

void process(X509 *cert) {
    char *cn = get_cn(cert);
    printf("%s", cn);       // NULL propagated silently from inner call
}
```

```c
// SAFE
char *get_cn(X509 *cert) {
    X509_NAME *name = X509_get_subject_name(cert);
    if (name == NULL) return NULL;
    return strdup(name_string);
}

void process(X509 *cert) {
    char *cn = get_cn(cert);
    if (cn == NULL) { handle_error(); return; }
    printf("%s", cn);
}
```

---

### Pattern 11: C++ — Unchecked `dynamic_cast` / `std::get_if`

`dynamic_cast` to a pointer type returns `nullptr` if the cast fails. `std::get_if` returns `nullptr` if the variant does not hold the requested type.

```cpp
// VULNERABLE
Base *base = get_object();
Derived *d = dynamic_cast<Derived*>(base);
d->method();                // crash if base is not a Derived

// VULNERABLE — std::get_if
auto *val = std::get_if<int>(&variant);
*val = 42;                  // nullptr if variant does not hold int
```

```cpp
// SAFE
Derived *d = dynamic_cast<Derived*>(base);
if (d == nullptr) { handle_error(); return; }
d->method();
```

---

### Pattern 12: C++ — Iterator / `find` Result Not Checked

`std::map::find`, `std::find`, etc. return `end()` when the key is not found. Dereferencing `end()` is undefined behavior.

```cpp
// VULNERABLE
auto it = my_map.find(key);
return it->second;          // UB if key not found — it == my_map.end()
```

```cpp
// SAFE
auto it = my_map.find(key);
if (it == my_map.end()) { handle_error(); return; }
return it->second;
```

---

### Pattern 13: Uninitialized Out-Parameter

A pointer is passed as an out-parameter but the callee does not set it on error, leaving it uninitialized or NULL.

```c
// VULNERABLE
int *out;                   // uninitialized
int rc = get_value(&out);   // sets *out only on success
printf("%d", *out);         // crash if get_value failed and rc not checked
```

```c
// SAFE
int *out = NULL;
int rc = get_value(&out);
if (rc != SUCCESS || out == NULL) { handle_error(); return; }
printf("%d", *out);
```

---

### Pattern 14: `strtok` Returning NULL on Exhaustion

`strtok` returns `NULL` when no more tokens remain. Continuing to use the result past the last token crashes.

```c
// VULNERABLE
char *token = strtok(input, ",");
while (1) {
    process(token);         // crash on iteration after last token
    token = strtok(NULL, ",");
}
```

```c
// SAFE
char *token = strtok(input, ",");
while (token != NULL) {
    process(token);
    token = strtok(NULL, ",");
}
```

---

## Detection: Semgrep Rules

### Pattern Rules (semgrep OSS)

```yaml
rules:
  # Pattern 1: Return value discarded (heuristic regex)
  - id: discarded-pointer-function-return
    message: >
      Return value of `$FUNC()` is discarded. If this function returns a pointer
      or status, callers must check the result before using any output buffers.
    severity: WARNING
    languages: [c, cpp]
    metadata:
      cwe: CWE-252
    patterns:
      - pattern: $FUNC(...);
      - pattern-not: $VAR = $FUNC(...);
      - pattern-not: return $FUNC(...);
      - pattern-not: if ($FUNC(...)) { ... }
      - pattern-not: if (!$FUNC(...)) { ... }
      - pattern-not: if ($FUNC(...) == NULL) { ... }
      - pattern-not: if ($FUNC(...) != NULL) { ... }
      - metavariable-regex:
          metavariable: $FUNC
          regex: (?i).*(get|alloc|new|create|open|dup|strdup|find|lookup|load|read|parse|oneline|print_ex).*

  # Pattern 2: Assigned pointer used without NULL check (heuristic regex)
  - id: unchecked-pointer-before-use
    message: >
      Pointer `$PTR` returned by `$FUNC()` is used without a NULL check.
      Dereferencing or passing a NULL pointer causes undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $SINK($PTR, ...);
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR != NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          assert($PTR);
      - metavariable-regex:
          metavariable: $FUNC
          regex: (?i).*(get|alloc|new|create|open|dup|strdup|find|lookup|load|read|parse|malloc|calloc).*

  # Pattern 3: Chained call — inner result not checked (heuristic regex)
  - id: unchecked-chained-call-result
    message: >
      Return value of `$INNER()` is passed directly to `$OUTER()` without a NULL check.
      If `$INNER()` returns NULL on failure, this causes undefined behavior in `$OUTER()`.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: $OUTER($INNER(...), ...)
      - metavariable-regex:
          metavariable: $INNER
          regex: (?i).*(get|alloc|new|create|open|dup|find|lookup|load|read|parse).*
      - metavariable-regex:
          metavariable: $OUTER
          regex: (?!.*(assert|log|print|debug|error|warn|free|check).*).*

  # Pattern 4: Pointer parameter dereferenced without NULL check
  - id: pointer-param-dereferenced-without-null-check
    message: >
      Pointer parameter `$STR` is dereferenced without a prior NULL check.
      Callers may pass NULL, causing undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: CWE-476
    patterns:
      - pattern: |
          $RET $FUNC(... , $TYPE *$STR, ...) {
            ...
            *$STR;
            ...
          }
      - pattern-not: |
          $RET $FUNC(... , $TYPE *$STR, ...) {
            if ($STR == NULL) { ... }
            ...
          }
      - pattern-not: |
          $RET $FUNC(... , $TYPE *$STR, ...) {
            if (!$STR) { ... }
            ...
          }

  # Pattern 5: malloc/calloc result not checked
  - id: unchecked-malloc-result
    message: >
      Return value of `$FUNC()` is not checked for NULL.
      Memory allocation functions return NULL on failure; using the result causes a crash.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $USE($PTR, ...);
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) { ... }
      - metavariable-regex:
          metavariable: $FUNC
          regex: ^(malloc|calloc|aligned_alloc|valloc)$

  # Pattern 5b: realloc overwrites original pointer — memory leak on failure
  - id: realloc-overwrites-original-pointer
    message: >
      `realloc()` result assigned directly to the original pointer.
      If realloc fails it returns NULL, overwriting the original pointer and causing a memory leak.
      Use a temporary pointer, check for NULL, then assign.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: CWE-476
    pattern: $PTR = realloc($PTR, ...);

  # Pattern 6: Struct member access on unchecked pointer (heuristic regex)
  - id: unchecked-struct-member-access
    message: >
      Pointer `$PTR` is used to access member `$FIELD` without a NULL check.
      If `$FUNC()` returns NULL, this causes a crash.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $PTR->$FIELD;
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) { ... }
      - metavariable-regex:
          metavariable: $FUNC
          regex: (?i).*(get|find|lookup|alloc|new|create|open|load|read|parse).*

  # Pattern 7: String search result used without NULL check
  - id: unchecked-string-search-result
    message: >
      Result of `$FUNC()` is used without a NULL check.
      String search functions return NULL when the pattern is not found.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $USE($PTR, ...);
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) { ... }
      - metavariable-regex:
          metavariable: $FUNC
          regex: ^(strstr|strchr|strrchr|strpbrk|memmem)$

  # Pattern 8: getenv / fopen result not checked
  - id: unchecked-system-function-result
    message: >
      Return value of `$FUNC()` is not checked for NULL.
      System functions return NULL when the resource does not exist or the call fails.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    patterns:
      - pattern: |
          $TYPE *$PTR = $FUNC(...);
          ...
          $USE($PTR, ...);
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR == NULL) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if (!$PTR) { ... }
      - pattern-not: |
          $TYPE *$PTR = $FUNC(...);
          ...
          if ($PTR) { ... }
      - metavariable-regex:
          metavariable: $FUNC
          regex: ^(getenv|fopen|fdopen|freopen|opendir|dlopen|popen)$

  # Pattern 11: C++ unchecked dynamic_cast
  - id: unchecked-dynamic-cast
    message: >
      Result of `dynamic_cast` is used without a nullptr check.
      If the cast fails at runtime it returns nullptr, causing a crash on member access.
    severity: ERROR
    languages: [cpp]
    metadata:
      cwe: CWE-476
    patterns:
      - pattern: |
          $TYPE *$PTR = dynamic_cast<$TYPE *>($OBJ);
          ...
          $PTR->$METHOD(...);
      - pattern-not: |
          $TYPE *$PTR = dynamic_cast<$TYPE *>($OBJ);
          ...
          if ($PTR == nullptr) { ... }
      - pattern-not: |
          $TYPE *$PTR = dynamic_cast<$TYPE *>($OBJ);
          ...
          if (!$PTR) { ... }

  # Pattern 11b: C++ unchecked std::get_if
  - id: unchecked-get-if-result
    message: >
      Result of `std::get_if` is used without a nullptr check.
      If the variant does not hold the requested type, `std::get_if` returns nullptr,
      and dereferencing the result causes undefined behavior.
    severity: ERROR
    languages: [cpp]
    metadata:
      cwe: CWE-476
    patterns:
      - pattern: |
          auto *$PTR = std::get_if<$TYPE>(&$VAR);
          ...
          *$PTR;
      - pattern-not: |
          auto *$PTR = std::get_if<$TYPE>(&$VAR);
          ...
          if ($PTR == nullptr) { ... }
      - pattern-not: |
          auto *$PTR = std::get_if<$TYPE>(&$VAR);
          ...
          if (!$PTR) { ... }

  # Pattern 12: C++ map::find result not checked
  - id: unchecked-map-find-result
    message: >
      Result of `$MAP.find()` is used without checking against `end()`.
      Dereferencing `end()` is undefined behavior.
    severity: ERROR
    languages: [cpp]
    metadata:
      cwe: CWE-476
    patterns:
      - pattern: |
          auto $IT = $MAP.find(...);
          ...
          $IT->$FIELD;
      - pattern-not: |
          auto $IT = $MAP.find(...);
          ...
          if ($IT == $MAP.end()) { ... }
      - pattern-not: |
          auto $IT = $MAP.find(...);
          ...
          if ($IT != $MAP.end()) { ... }

  # Pattern 14: strtok loop without NULL check
  - id: strtok-loop-without-null-check
    message: >
      `strtok` is called in a loop without checking for NULL.
      When tokens are exhausted `strtok` returns NULL; passing NULL to the loop body causes a crash.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    pattern: |
      while (1) {
        ...
        strtok(NULL, ...);
        ...
      }
```

---

### Taint Rules (semgrep Pro)

Cover inter-procedural flow (patterns 9, 10) and indirect dereferences via intermediate pointer copies (pattern 4 variant).

```yaml
rules:
  # Patterns 9, 10: NULL propagates across function boundaries
  - id: null-pointer-unchecked-taint
    mode: taint
    message: >
      Value from `$SOURCE` flows into `$SINK` without a NULL check.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    pattern-sources:
      - patterns:
          - pattern: $FUNC(...)
          - metavariable-regex:
              metavariable: $FUNC
              regex: (?i).*(get|alloc|new|create|open|find|lookup|load|read|parse|malloc|calloc|getenv|fopen).*
    pattern-sanitizers:
      - pattern: if (!$X) { ... }
      - pattern: if ($X == NULL) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if ($X) { ... }
      - pattern: assert($X)
    pattern-sinks:
      - patterns:
          - pattern: $FUNC($X, ...)
          - metavariable-regex:
              metavariable: $FUNC
              regex: (?i).*(oneline|print|strstr|strcmp|strlen|memcpy|use|process|strchr|fread|fwrite).*

  # Pattern 13: Uninitialized out-parameter — callee may not set pointer on error paths
  - id: uninitialized-out-param-taint
    mode: taint
    message: >
      Out-parameter `$OUT` may not be assigned on all paths inside the callee.
      Using `*$OUT` without first checking the return code causes undefined behavior.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-457, CWE-476]
    pattern-sources:
      - pattern: |
          $RET $CALLEE(..., $TYPE **$OUT, ...) {
            ...
          }
    pattern-sanitizers:
      - patterns:
          - pattern: |
              $RC = $CALLEE(...);
              if ($RC != $SUCCESS) { ... }
      - patterns:
          - pattern: |
              $RC = $CALLEE(...);
              if ($RC == $ERR) { ... }
      - pattern: if ($X == NULL) { ... }
      - pattern: if (!$X) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if ($X) { ... }
    pattern-sinks:
      - pattern: "*$X"
      - pattern: $X->$FIELD

  # Pattern 4 indirect variant: pointer parameter flows into dereference via copy
  - id: pointer-param-indirect-deref-taint
    mode: taint
    message: >
      Pointer parameter `$STR` is dereferenced (possibly indirectly) without a NULL check.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: CWE-476
    pattern-sources:
      - pattern: |
          $RET $FUNC(... , $TYPE *$STR, ...) {
            ...
          }
    pattern-sanitizers:
      - pattern: if ($X == NULL) { ... }
      - pattern: if (!$X) { ... }
      - pattern: if ($X) { ... }
    pattern-sinks:
      - pattern: "*$X"
      - pattern: "$X[...]"

  # Pattern 12: C++ map::find result flows across function boundaries to dereference
  - id: unchecked-map-find-taint
    mode: taint
    message: >
      Result of `$MAP.find()` flows to a dereference without an `end()` check.
      Dereferencing `end()` is undefined behavior.
    severity: ERROR
    languages: [cpp]
    metadata:
      cwe: CWE-476
    pattern-sources:
      - pattern: $MAP.find(...)
    pattern-sanitizers:
      - pattern: if ($X == $MAP.end()) { ... }
      - pattern: if ($X != $MAP.end()) { ... }
    pattern-sinks:
      - pattern: $X->$FIELD
      - pattern: "(*$X).$FIELD"
      - pattern: "*$X"

  # Pattern 14: strtok/strtok_r/strsep result flows across function boundaries without NULL check
  - id: strtok-result-null-check-taint
    mode: taint
    message: >
      Result of `$FUNC()` flows to a use without a NULL check.
      When tokens are exhausted these functions return NULL; using the result causes a crash.
    severity: ERROR
    languages: [c, cpp]
    metadata:
      cwe: [CWE-476, CWE-690]
    pattern-sources:
      - patterns:
          - pattern: $FUNC(...)
          - metavariable-regex:
              metavariable: $FUNC
              regex: ^(strtok|strtok_r|strsep)$
    pattern-sanitizers:
      - pattern: if ($X == NULL) { ... }
      - pattern: if (!$X) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if ($X) { ... }
    pattern-sinks:
      - pattern: $FUNC($X, ...)
      - pattern: "*$X"
      - pattern: $X->$FIELD
      - pattern: "$X[...]"
```


---

## Out-of-Scope: CWE-789 (Memory Allocation with Excessive Size Value)

CWE-789 is related to `malloc`/`calloc` but belongs to a different vulnerability family and is intentionally not covered here.

**CWE hierarchy:** CWE-789 → CWE-119 (Improper Restriction of Operations within Bounds of a Memory Buffer), not CWE-476.

**Why it is not a null pointer issue:** The null return from `malloc` is only one possible outcome of an excessive size argument. The more dangerous path is when the OS succeeds with a wrapped-around size:

```c
// n comes from untrusted input — no bounds check
size_t n = atoi(user_input);
char *buf = malloc(n * sizeof(int));  // if n * sizeof(int) overflows → tiny buffer allocated
memcpy(buf, src, n * sizeof(int));    // heap overflow — NOT a null pointer issue
```

The two failure paths and their CWEs:

| Path | Outcome | CWE |
|---|---|---|
| `malloc` returns `NULL` (size too large, OS rejects) | NULL dereference if unchecked | CWE-476 / CWE-690 (already covered by Pattern 5) |
| `malloc` succeeds with integer-overflowed size (tiny buffer) | Heap buffer overflow on subsequent write | CWE-122 — out of scope here |

**Where it belongs:** CWE-789 should be detected in an integer overflow / memory allocation ruleset, using a taint rule that tracks untrusted values flowing into allocation size arguments.

---

## Toolchain: Building a Project-Specific Allowlist
In the Toolchain approach, "X509_NAME_oneline" is an OpenSSL-specific function name that leaked in from the doc's motivating example. It has no place in a project-agnostic generated rule — it belongs in pattern-sources(as a nullable function) if discovered by the toolchain, not hardcoded in pattern-sinks.  
   
In the rule "id: discarded-pointer-function-return",  
```regex: (?i).*(get|alloc|new|create|open|dup|strdup|find|lookup|load|read|parse|oneline|print_ex).*```                                                         

| Term | Rationale |
|---|---|
| get | X509_get_issuer_name, getenv, pthread_getspecific — getters often return NULL on failure |
| alloc | malloc, calloc, custom allocators — allocation can fail                                  |
| new | C++ style allocators, factory functions                                                  |
| create | Factory pattern — returns NULL if resource creation fails                                |
| open | fopen, opendir, dlopen — NULL on missing resource                                        |
| dup | strdup, strndup — calls malloc internally, can return NULL                               |
| strdup | Explicit inclusion since it's a very common source                                       |
| find | strstr, strchr, map lookups — NULL when not found                                        |
| lookup | Hash/table lookups — NULL when key absent                                                |
| load | dlopen, config/file loaders — NULL on failure                                            |
| read | Parsers, stream readers — NULL on EOF or error                                           |
| parse | Parsers that return NULL on malformed input                                              |
| oneline | X509_NAME_oneline specifically — the motivating example                                  |
| print_ex | OpenSSL print functions that can fail                                                    |

It's a **heuristic** based on common C/C++ naming conventions for functions that typically return a pointer that can be NULL.  
The problem is it's both directions:  
  - **Overfitting** — get_version(), create_label(), new_id() may never return NULL but still match  
  - **Underfitting** — extract_field(), fetch_token(), resolve_path() return NULL but don't match                                                                                                                          
This is exactly why **find_nullable_functions** exists — to replace this guess with functions that provably have a return NULL path in your codebase.                                                                  
Rather than relying on heuristic regex patterns for function names, use the provided toolchain to derive an exact allowlist from your codebase.

### Files

| File | Purpose |
|---|---|
| `find-nullable-functions.yaml` | Semgrep rule — discovers all functions with a `return NULL` / `return nullptr` path |
| `find-nonnull-annotated-functions.yaml` | Semgrep rule — discovers functions annotated `returns_nonnull`; excluded from nullable list |
| `find-null-safe-functions.yaml` | Semgrep rule — discovers functions that check pointer params for NULL; excluded from `$OUTER` in Rule 4 |
| `build_nullable_allowlist.py` | Script — parses combined results, generates precise rules with exact allowlists |
| `null_ptr_generated.yaml` | Output — generated semgrep rules (do not edit manually) |


### Workflow

```
Step 1: Discover nullable, non-null, and null-safe functions in one pass
─────────────────────────────────────────────────────────────────────
semgrep --config panw.c.general.find-nullable-functions.yaml \
        --config panw.c.general.find-nonnull-annotated-functions.yaml \
        --config panw.c.general.find-null-safe-functions.yaml \
        --json <src_dir> \
    | python build_nullable_allowlist.py --output null_ptr_generated.yaml

Step 2: Review the discovered lists
─────────────────────────────────────────────────────────────────────
semgrep --config panw.c.general.find-nullable-functions.yaml \
        --config panw.c.general.find-nonnull-annotated-functions.yaml \
        --config panw.c.general.find-null-safe-functions.yaml \
        --json <src_dir> \
    | python build_nullable_allowlist.py --list-only

Step 3: Run generated rules against the codebase
─────────────────────────────────────────────────────────────────────
semgrep --config null_ptr_generated.yaml <src_dir>

Step 4: Annotate confirmed non-null functions to exclude them
─────────────────────────────────────────────────────────────────────
// In source: mark functions that can never return NULL
char *get_version(void) __attribute__((returns_nonnull));

// Re-run Step 1 — annotated functions are automatically excluded from sources
// and null-safe functions are automatically excluded from $OUTER in Rule 4
```


### What the script generates

The generated `null_ptr_generated.yaml` replaces the heuristic regex:

```yaml
# Heuristic (overfitting — misses non-matching names)
regex: (?i).*(get|alloc|new|create|open).*

# Generated (exact — derived from actual return NULL sites)
regex: '^(X509_get_issuer_name|find_node|get_cn|parse_config)$'
```

Four rules are generated automatically, replacing their heuristic counterparts:

| Generated rule (in `null_ptr_generated.yaml`) | Heuristic rule to drop |
|---|---|
| `generated-discarded-nullable-return` | `discarded-pointer-function-return` |
| `generated-unchecked-nullable-pointer-use` | `unchecked-pointer-before-use` |
| `generated-unchecked-struct-member-access` | `unchecked-struct-member-access` |
| `generated-unchecked-chained-nullable-call` | `unchecked-chained-call-result` |
| `generated-null-pointer-unchecked-taint` | `null-pointer-unchecked-taint` |

The generated taint rule (Rule 5) combines project-specific nullable functions discovered by the toolchain with a fixed set of stdlib nullable functions (`malloc`, `calloc`, `strdup`, `getenv`, `fopen`, `strstr`, `strchr`, etc.), replacing the heuristic regex in `null-pointer-unchecked-taint` with an exact source list.

> Do **not** run the heuristic rules alongside the generated rules — doing so produces duplicate findings and reintroduces the false positives the toolchain was designed to eliminate.
>
> **Exception:** keep the heuristic rules scoped to third-party library headers where source is unavailable for scanning and `find_nullable_functions` cannot discover nullable functions.




### Fitting trade-offs across all patterns

The heuristic regex and the fixed stdlib lists have opposite problems:

| Problem | Affects | Symptom |
|---|---|---|
| **Overfitting** (false positives) | Patterns 1–3, 6 — heuristic regex | Matches function names that happen to contain `get`/`alloc`/etc. but never return NULL |
| **Underfitting** (false negatives) | Patterns 5, 7, 8, 11, 12, 14 — fixed stdlib lists | Misses project-specific wrappers and variants with identical semantics |

The toolchain solves overfitting for project-specific functions by replacing the heuristic regex with an exact list. For stdlib patterns, address underfitting by extending the fixed lists with known wrappers in your codebase:

| Pattern | Common missed variants |
|---|---|
| 5 (`malloc`/`calloc`) | `xmalloc`, `g_malloc`, `my_alloc`, `safe_malloc` |
| 7 (`strstr`/`strchr`) | Custom search functions with same NULL-on-not-found semantics |
| 8 (`getenv`/`fopen`) | `open()` (returns −1), `mmap()` (returns `MAP_FAILED`), platform-specific I/O |
| 11 (`dynamic_cast`) | Smart pointer `.get()` returning `nullptr`, custom RTTI systems |
| 12 (`map::find`) | `unordered_map`, `multimap`, and other STL/custom containers |
| 14 (`strtok`) | `strtok_r`, `strsep` — same token-exhaustion behavior |

When using the toolchain, null_ptr_generated.yaml replaces the heuristic rule entirely for patterns 1, 2, 3, and 6. Running both would cause:  
  - Duplicate findings for functions in your codebase  
  - Extra false positives from the heuristic on top of the exact list


  
### Refresh cadence

Re-run the toolchain whenever new functions are added or existing ones are modified. The generated file is clearly marked `AUTO-GENERATED` and should not be edited manually.


---

## Detection Coverage Summary

| Pattern | Description | Vulnerable Example | OSS Rule ID | Pro Taint Rule ID | Coverage | Confidence | `find_nullable_functions` |
|---|---|---|---|---|---|---|---|
| 1 | Discarded return value | `X509_NAME_oneline(issuer, buf, 1024);` | `discarded-pointer-function-return` | — | OSS only → **Generated OSS only** (taint cannot track discarded returns) | Medium — heuristic regex on function names; rises to High with `find_nullable_functions` | **Replaces** heuristic rule — drop `discarded-pointer-function-return` when using toolchain |
| 2 | Assigned pointer, no NULL check (intra) | `char *p = get_data(); use(p);` | `unchecked-pointer-before-use` | `null-pointer-unchecked-taint` | Both → **Generated Both** | Medium — heuristic regex; `pattern-not` may miss uncommon sanitizer forms | **Replaces** heuristic rule — drop `unchecked-pointer-before-use` when using toolchain |
| 2 | Assigned pointer, no NULL check (cross-file) | return value of `get_data()` passed to another file unchecked | — | `generated-null-pointer-unchecked-taint` | Pro only → **Generated Pro** | Medium — taint may over-approximate across file boundaries | **Replaces** heuristic rule |
| 3 | Chained call without NULL check | `X509_NAME_oneline(X509_get_issuer_name(c), buf, 1024);` | `unchecked-chained-call-result` | — | OSS only → **Generated OSS only** (taint cannot track ephemeral inner value) | Medium → **High** with toolchain (`$INNER` exact, `$OUTER` excludes null-safe functions) | **Replaces** heuristic rule — `$INNER` uses exact nullable list; `$OUTER` excludes functions discovered by `find-null-safe-functions` |
| 4 | Pointer param direct dereference | `size_t f(char *str) { return *str; }` | `pointer-param-dereferenced-without-null-check` | `pointer-param-indirect-deref-taint` | Both (unchanged) | Medium — callers may guarantee non-NULL by convention; no caller-side analysis | No — targets parameter input, not return values |
| 4 | Pointer param indirect dereference (`p = str; *p`) | `const char *p = str; *p;` | — | `pointer-param-indirect-deref-taint` | Pro only (unchanged) | Medium | No |
| 5 | Failed `malloc`/`calloc` | `char *buf = malloc(1024); strcpy(buf, s);` | `unchecked-malloc-result` | `null-pointer-unchecked-taint` | Both → **Both (stdlib in generated taint sources)** | High — exact stdlib names; unchecked malloc result is always wrong | No — fixed stdlib names included in generated taint sources automatically |
| 5b | `realloc` overwrites original pointer | `buf = realloc(buf, n);` | `realloc-overwrites-original-pointer` | — | OSS only (unchanged) | High — structural pattern `$PTR = realloc($PTR, ...)` is always a bug | No |
| 6 | Struct member access on unchecked pointer | `node = find_node(l, k); node->value = 42;` | `unchecked-struct-member-access` | `null-pointer-unchecked-taint` | Both → **Generated Both** | Medium — heuristic regex on function names | **Replaces** heuristic rule — drop `unchecked-struct-member-access` when using toolchain |
| 7 | `strstr`/`strchr` result not checked | `char *p = strstr(buf, "key="); p += 4;` | `unchecked-string-search-result` | `null-pointer-unchecked-taint` | Both → **Both (stdlib in generated taint sources)** | High — exact stdlib names; arithmetic on result without check is always a crash | No — fixed stdlib names included in generated taint sources automatically |
| 8 | `getenv`/`fopen` result not checked | `char *h = getenv("HOME"); strlen(h);` | `unchecked-system-function-result` | `null-pointer-unchecked-taint` | Both → **Both (stdlib in generated taint sources)** | High — exact stdlib names; NULL return is documented and common | No — fixed stdlib names included in generated taint sources automatically |
| 9 | Conditional NULL (only set in some paths) | `char *r = NULL; if (c) r = alloc(); use(r);` | — | `null-pointer-unchecked-taint` | Pro only → **Generated Pro (improved sources)** | Medium — taint may flag cases where all real callers always satisfy the condition | No — dataflow, not function-name driven; benefits from improved taint sources |
| 10 | NULL propagation across function calls | `char *cn = get_cn(cert); printf("%s", cn);` | — | `null-pointer-unchecked-taint` | Pro only → **Generated Pro (improved sources)** | Medium — inter-procedural taint may over-approximate through wrapper chains | No — dataflow, not function-name driven; benefits from improved taint sources |
| 11a | C++ unchecked `dynamic_cast` | `Derived *d = dynamic_cast<Derived*>(b); d->method();` | `unchecked-dynamic-cast` | — | OSS only (unchanged) | High — cast failure is well-defined; missing nullptr check is always unsafe | No — language construct, not a named function |
| 11b | C++ unchecked `std::get_if` | `auto *v = std::get_if<int>(&var); *v = 42;` | `unchecked-get-if-result` | — | OSS only (unchanged) | High — nullptr return on type mismatch is well-defined | No — language construct, not a named function |
| 12 | C++ iterator `find()` result not checked | `auto it = m.find(k); return it->second;` | `unchecked-map-find-result` | `unchecked-map-find-taint` | Both (unchanged) | High — dereferencing `end()` is always UB | No — fixed stdlib names |
| 13 | Uninitialized out-parameter (CWE-457) | `int *out; get_val(&out); printf("%d", *out);` | — | `uninitialized-out-param-taint` | Pro only (partial — return-code sanitizer required, unchanged) | Low — partial coverage; return-code check sanitizer may miss non-standard error conventions | No — dataflow, not function-name driven |
| 14 | `strtok`/`strtok_r`/`strsep` exhaustion | `while(1) { use(tok); tok = strtok(NULL, ","); }` | `strtok-loop-without-null-check` | `strtok-result-null-check-taint` | Both (unchanged) | High (OSS) / Medium (taint — may flag intentional sentinel loops) | No — fixed stdlib names |





> **OSS-only patterns** — covered by OSS rule but no Pro taint rule is possible:
> - Pattern 3 — inner call value is ephemeral (never assigned to a variable taint can track)
> - Pattern 5b — `realloc` overwrite is structural, not a data flow
> - Patterns 11a/11b — `dynamic_cast` / `std::get_if` are language constructs with no taintable source
>
> - All other patterns with `—` in the OSS column are covered by their Pro taint rule.
> - Every pattern now has at least one rule. The note correctly distinguishes between "OSS-only" (has OSS but taint can't be added) and "Pro-only" (has taint but OSS can't detect it) — no pattern is truly uncovered.

---
## References

- [CWE-476: NULL Pointer Dereference](https://cwe.mitre.org/data/definitions/476.html)
- [CWE-252: Unchecked Return Value](https://cwe.mitre.org/data/definitions/252.html)
- [CWE-457: Use of Uninitialized Variable](https://cwe.mitre.org/data/definitions/457.html)
- [CWE-690: Unchecked Return Value to NULL Pointer Dereference](https://cwe.mitre.org/data/definitions/690.html)
- [OpenSSL X509_NAME_oneline documentation](https://www.openssl.org/docs/man3.0/man3/X509_NAME_oneline.html)
- [Semgrep taint mode documentation](https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/)


---

## 'return nullptr;' is not same as 'return NULL;'  
In C++11 and later, nullptr is preferred and safer:

  - nullptr — a typed null pointer constant (std::nullptr_t). Cannot be accidentally used as an integer.
  - NULL — typically defined as 0 or (void*)0. Can implicitly convert to int, causing ambiguity in overloaded functions.

  Example where they differ:

  void foo(int);
  void foo(char*);

  foo(NULL);    // Ambiguous or calls foo(int) — not what you want
  foo(nullptr); // Unambiguously calls foo(char*)

In C, nullptr doesn't exist (until C23). NULL is the standard null pointer constant there.  




