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
  # Pattern 1: Return value discarded
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

  # Pattern 2: Assigned pointer used without NULL check
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

  # Pattern 3: Chained call — inner result not checked
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

  # Patterns 5, 7, 8 (combined): stdlib nullable result not checked
  # Covers:
  #   - Memory allocation: malloc, calloc, aligned_alloc, valloc
  #   - String search:     strstr, strchr, strrchr, strpbrk, memmem
  #   - System/env/IO:     getenv, fopen, fdopen, freopen, opendir, dlopen, popen
  - id: unchecked-stdlib-nullable-result
    message: >
      Return value of `$FUNC()` is used without a NULL check.
      Covered stdlib categories —
      memory allocation (malloc, calloc, aligned_alloc, valloc): returns NULL on allocation failure;
      string search (strstr, strchr, strrchr, strpbrk, memmem): returns NULL when pattern not found;
      system/env/IO (getenv, fopen, fdopen, freopen, opendir, dlopen, popen): returns NULL when
      the variable, file, or resource does not exist or cannot be opened.
      Using the result without checking causes a crash.
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
          regex: ^(malloc|calloc|aligned_alloc|valloc|strstr|strchr|strrchr|strpbrk|memmem|getenv|fopen|fdopen|freopen|opendir|dlopen|popen)$

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

  # Pattern 6: Struct member access on unchecked pointer
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


| Pattern | $FUNC regex | Sanitizers |  Sink |
|---|---|---|---|                                          
|2 | `heuristic get│alloc│...`     | same 5     | $SINK($PTR, ...)         |
|5 | `exact ^(malloc│calloc│...)$` | same 5     | $USE($PTR, ...)          |
|6 | `heuristic get│find│...`      | same 3     | $PTR->$FIELD ← different |
|7 | `exact ^(strstr│strchr│...)$` | same 5     | $USE($PTR, ...)          |
|8 | `exact ^(getenv│fopen│...)$`  | same 5     | $USE($PTR, ...)          |                                                                                                                                   

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
    options:
      interfile: true   # required — patterns 2 (inter) and 10 track NULL across file boundaries
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
    options:
      interfile: true   # required — callee (source) and caller (sink) are commonly in separate files
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
    # options.interfile not set — source (parameter) and sink (dereference) are within the same function body
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
    # options.interfile not set — most map::find uses are intra-file; enable if cross-file iterator passing is observed
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
    # options.interfile not set — most strtok token usage is intra-file; enable if tokens are passed across file boundaries
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

**Can I drop oss mode rule of a pattern if its pro mode rule exists?**   

Not fully — it depends on the pattern. The key issue is sink breadth:

  OSS rules use unconstrained sinks — any function call or dereference:
  ```
  $SINK($PTR, ...)   # matches any function
  $PTR->$FIELD       # matches any member access
  ```

  Pro taint rules constrain sinks to a specific regex:
  ```
  pattern-sinks:
    - patterns:
        - pattern: $FUNC($X, ...)
        - metavariable-regex:
            metavariable: $FUNC
            regex: (?i).*(print|strstr|strcmp|strlen|memcpy|...).*
  ```

So if the pointer flows into a function not in the sink regex, taint misses it but OSS catches it.
| Pattern | Pro subsumes OSS? | Reason | 
|---|---|---|
| 1       | No                | Taint cannot track discarded return values                                                         |
| 2       | No                | Taint sinks are constrained; OSS catches any $SINK($PTR, ...)                                      |
| 3       | No                | Taint cannot track ephemeral inner call value                                                      |
| 4       | Yes               | Taint source is the parameter; sink is *$X / $X[...] — covers both direct and indirect dereference |
| 5/7/8   | No                | Taint sinks constrained; OSS catches any use of the pointer                                        |
| 5b      | No                | Structural pattern — no data flow to taint                                                         |
| 6       | No                | Taint sinks don't include $PTR->$FIELD                                                             |
| 11a/11b | No                | Language constructs — no taintable source                                                          |
| 12      | Yes               | Taint source=find(), sink=$X->$FIELD — covers intra-file and cross-file                            |
| 14      | Partial           | Taint covers more cases; OSS while(1) pattern catches structurally without sink constraint         |

Practical conclusion: for patterns 4 and 12, you could drop the OSS rule and rely solely on Pro taint. For all others, OSS and Pro taint are complementary — dropping OSS would lose findings where the pointer flows to unconstrained sinks.  
  
---    

| Rule | Source | Sanitizer | Sink | Language |
|---|---|---|---|---|
| null-pointer-unchecked-taint | function call (heuristic regex) | NULL checks | function call (heuristic regex) | c, cpp |
| uninitialized-out-param-taint | `$TYPE **$OUT` double-pointer param | return-code check + NULL checks | *$X, $X->$FIELD | c, cpp |
| pointer-param-indirect-deref-taint | `$TYPE *$STR` single pointer param | NULL checks only | *$X, $X[...] | c, cpp |
| unchecked-map-find-taint | `$MAP.find(...)` | `end()` check | $X->$FIELD, *$X | cpp only |                                                
| strtok-result-null-check-taint | `strtok│strtok_r│strsep` exact | NULL checks | $FUNC($X,...), *$X, $X->$FIELD, $X[...] | c, cpp |                              
---

| Rule | interfile | Rationale | 
|---|---|---|                                                                                          
| null-pointer-unchecked-taint       | true      | Required — patterns 2/10 track NULL across file boundaries |
| uninitialized-out-param-taint      | true      | Required — callee and caller commonly in separate files    |
| pointer-param-indirect-deref-taint | false     | Not needed — source and sink within the same function body |
| unchecked-map-find-taint           | false     | Optional — enable only if iterators are passed cross-file  |
| strtok-result-null-check-taint     | false     | Optional — enable only if tokens are passed cross-file     |                                                  

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
semgrep --config find-nullable-functions.yaml \
        --config find-nonnull-annotated-functions.yaml \
        --config find-null-safe-functions.yaml \
        <src_dir> --json \
    | python3 build_nullable_allowlist.py --output null_ptr_generated.yaml

Step 2: Review the discovered lists
─────────────────────────────────────────────────────────────────────
semgrep --config find-nullable-functions.yaml \
        --config find-nonnull-annotated-functions.yaml \
        --config find-null-safe-functions.yaml \
        <src_dir> --json \
    | python3 build_nullable_allowlist.py --list-only

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

The generated taint rule (Rule 5) combines project-specific nullable functions discovered by the toolchain with a fixed set of stdlib nullable functions (`malloc`, `calloc`, `strdup`, `getenv`, `fopen`, `strstr`, `strchr`, etc.) and a seeded set of known third-party nullable functions, replacing the heuristic regex in `null-pointer-unchecked-taint` with an exact source list.

> Do **not** run the original rules alongside the generated rules — doing so produces duplicate findings and reintroduces the heuristic false positives the toolchain was designed to eliminate.

### ⚠️ Third-party library gap

`find_nullable_functions.yaml` only discovers functions whose **source code is scanned**. Third-party library functions (OpenSSL, libcurl, etc.) are compiled objects — their source is not present, so `find_nullable_functions` never discovers them and they are absent from the generated `exact_regex`.

**Example:** `X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024)` — `X509_get_issuer_name` returns `NULL` if the certificate has no issuer, but it is an OpenSSL function. The toolchain alone cannot detect this as a chained-call hazard.

The OpenSSL header provides no machine-readable nullability contract:

```c
// openssl/x509.h — bare pointer return, no annotation
X509_NAME *X509_get_issuer_name(const X509 *x);
```

There is no `_Nullable`, no SAL annotation, no `__attribute__` — nullability is documented in prose only but not expressed in the type system. This is the norm for most C libraries (OpenSSL, libcurl, sqlite, etc.).

#### Why automated discovery approaches fall short  
Explains why header scanning fails (no annotation) and why call-site inference fails (the only call site is the vulnerable one — no checked callers to learn from):                              
**Header annotation scanning** — looks for `_Nullable` / `_Ret_maybenull_` / `__nullable` in `.h` files. Does not work for OpenSSL-style headers that carry no annotations.

**Call-site inference** — looks for existing NULL checks after a function call in the scanned codebase, e.g.:

```c
X509_NAME *name = X509_get_issuer_name(cert);
if (name == NULL) { ... }   // inferred: function is nullable
```

This only works when **other callers in the same codebase already check** the return value. If the codebase consistently skips the check — which is exactly the bug being searched for — the rule discovers nothing. In the example above, the only call site is the vulnerable chained call with no assignment and no check.

#### Discovery approach coverage

| Scenario | `find_nullable_functions` | Header scan | Call-site inference | `KNOWN_THIRD_PARTY_NULLABLE` |
|---|---|---|---|---|
| 3rd party source code available (.c, .cpp) | ✅ | — | — | — |
| Header annotated (`_Nullable`) in third-party header files (.h) | — | ✅ | — | — |
| Some callers check, some don't | — | — | ✅ | — |
| No caller checks (all vulnerable) | — | — | ❌ | ✅ |
| Unannotated header, no checked callers | — | ❌ | ❌ | ✅ |

For unannotated third-party C libraries where the codebase has no NULL-checking call sites, `KNOWN_THIRD_PARTY_NULLABLE` is the only viable option. The manual cost is bounded — one entry per library function, not per call site.

#### Solution — `KNOWN_THIRD_PARTY_NULLABLE`

```python
KNOWN_THIRD_PARTY_NULLABLE: set[str] = {
    # OpenSSL — X509
    "X509_get_issuer_name",       # returns NULL if cert has no issuer
    "X509_get_subject_name",      # returns NULL if cert has no subject
    "X509_get_pubkey",            # returns NULL on failure
    # OpenSSL — BIO
    "BIO_new",                    # returns NULL on allocation failure
    "BIO_new_mem_buf",            # returns NULL on failure
    # OpenSSL — EVP
    "EVP_get_digestbyname",       # returns NULL if digest not found
    "EVP_MD_CTX_new",             # returns NULL on allocation failure
}
```

These functions are statically seeded and merged into:
- **Rules 1–4 `$FUNC`/`$INNER` regex** — catches discarded, unchecked-assigned, struct-member, and chained-call patterns involving third-party nullable returns
- **Rule 5 taint sources** — tracks NULL propagation from third-party returns through the codebase

Add new entries whenever a third-party library function is found to return NULL and appears in call sites without a check. Include a comment with the library name and the NULL condition.


**Assue all functions are nullable is the most conservative possible assumption — zero false negatives for third-party functions. But the false positive cost is severe.**  
The problem: you can't distinguish third-party from project at match time.  
Semgrep sees `$FUNC(...)` — it has no concept of which translation unit or library `$FUNC` belongs to. To implement "all third-party functions are nullable" you'd need a regex that matches every function name except the project-discovered ones. That regex would also match project functions not yet in the allowlist, internal helpers, etc.                                                                

False positive examples that would fire:

```c
// These never return NULL — they abort/exit on failure
SSL_CTX *ctx = SSL_CTX_new(TLS_method());    // fires — but libssl aborts on OOM
BIGNUM *bn = BN_new();                        // fires — but caller checks separately

// These return non-pointer types cast to pointer
const char *err = ERR_reason_error_string(e); // fires — but well-defined for known codes

// Project-internal nonnull functions not yet scanned
Config *cfg = get_global_config();            // fires — but annotated returns_nonnull
```

The real trade-off:

| Approach | False negatives | False positives  | Maintenance |
|---|---|---|---|                                            
| KNOWN_THIRD_PARTY_NULLABLE (current) | Misses unknown third-party functions | None | Add entries manually |                     
| Assume all third-party nullable | None | Very high — many third-party functions never return NULL | Must maintain an exclusion list instead | 
|Call-site inference | Misses unchecked call sites | Low | None |                       

"Assume all nullable" shifts the problem — instead of maintaining an inclusion list of nullable functions, you'd be maintaining an exclusion list of nonnull functions, which is larger and harder to keep complete.    

For security tooling specifically, high false positive rates cause alert fatigue and erode trust in the rules — teams start ignoring findings wholesale. KNOWN_THIRD_PARTY_NULLABLE keeps false positives at zero at the cost of bounded manual effort.  

---

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

| Pattern | Description | Vulnerable Example | OSS Rule ID | Pro Taint Rule ID | Coverage | Confidence | `find_nullable_functions` | Select Rule |
|---|---|---|---|---|---|---|---|---|
| 1 | Discarded return value | `X509_NAME_oneline(issuer, buf, 1024);` | `discarded-pointer-function-return` | — | OSS only → **Generated OSS only** (taint cannot track discarded returns) | Medium — heuristic regex on function names; rises to High with `find_nullable_functions` | **Replaces** heuristic rule — drop `discarded-pointer-function-return` when using toolchain | `generated-discarded-nullable-return` |
| 2 | Assigned pointer, no NULL check | `char *p = get_data(); use(p);` | `unchecked-pointer-before-use` | `null-pointer-unchecked-taint` | Both → **Generated Both** (OSS: intra-file; taint: intra + cross-file) | Medium — heuristic regex; `pattern-not` may miss uncommon sanitizer forms | **Replaces** heuristic rule — drop `unchecked-pointer-before-use` when using toolchain | `generated-unchecked-nullable-pointer-use` + `generated-null-pointer-unchecked-taint` |
| 3 | Chained call without NULL check | `X509_NAME_oneline(X509_get_issuer_name(c), buf, 1024);` | `unchecked-chained-call-result` | — | OSS only → **Generated OSS only** (taint cannot track ephemeral inner value) | Medium → **High** with toolchain (`$INNER` exact, `$OUTER` excludes null-safe functions) | **Replaces** heuristic rule — `$INNER` uses exact nullable list; `$OUTER` excludes functions discovered by `find-null-safe-functions` | `generated-unchecked-chained-nullable-call` |
| 4 | Pointer param dereferenced without NULL check | `size_t f(char *str) { return *str; }` / `const char *p = str; *p;` | `pointer-param-dereferenced-without-null-check` | `pointer-param-indirect-deref-taint` | Both (OSS: direct deref; taint: direct + indirect via copy) | Medium — callers may guarantee non-NULL by convention; no caller-side analysis | No — targets parameter input, not return values | `pointer-param-dereferenced-without-null-check` + `pointer-param-indirect-deref-taint` |
| 5/7/8 | Stdlib nullable result not checked (memory alloc, string search, system/IO) | `char *buf = malloc(1024); strcpy(buf, s);` / `char *p = strstr(buf, "key="); p += 4;` / `char *h = getenv("HOME"); strlen(h);` | `unchecked-stdlib-nullable-result` | `null-pointer-unchecked-taint` | Both → **Both (stdlib in generated taint sources)** | High — exact stdlib names; all three categories have well-defined NULL-on-failure semantics | No — fixed stdlib names included in generated taint sources automatically | `unchecked-stdlib-nullable-result` + `generated-null-pointer-unchecked-taint` |
| 5b | `realloc` overwrites original pointer | `buf = realloc(buf, n);` | `realloc-overwrites-original-pointer` | — | OSS only (unchanged) | High — structural pattern `$PTR = realloc($PTR, ...)` is always a bug | No | `realloc-overwrites-original-pointer` |
| 6 | Struct member access on unchecked pointer | `node = find_node(l, k); node->value = 42;` | `unchecked-struct-member-access` | `null-pointer-unchecked-taint` | Both → **Generated Both** | Medium — heuristic regex on function names | **Replaces** heuristic rule — drop `unchecked-struct-member-access` when using toolchain | `generated-unchecked-struct-member-access` + `generated-null-pointer-unchecked-taint` |
| 9 | Conditional NULL (only set in some paths) | `char *r = NULL; if (c) r = alloc(); use(r);` | — | `null-pointer-unchecked-taint` | Pro only → **Generated Pro (improved sources)** | Medium — taint may flag cases where all real callers always satisfy the condition | No — dataflow, not function-name driven; benefits from improved taint sources | `generated-null-pointer-unchecked-taint` |
| 10 | NULL propagation across function calls | `char *cn = get_cn(cert); printf("%s", cn);` | — | `null-pointer-unchecked-taint` | Pro only → **Generated Pro (improved sources)** | Medium — inter-procedural taint may over-approximate through wrapper chains | No — dataflow, not function-name driven; benefits from improved taint sources | `generated-null-pointer-unchecked-taint` |
| 11a | C++ unchecked `dynamic_cast` | `Derived *d = dynamic_cast<Derived*>(b); d->method();` | `unchecked-dynamic-cast` | — | OSS only (unchanged) | High — cast failure is well-defined; missing nullptr check is always unsafe | No — language construct, not a named function | `unchecked-dynamic-cast` |
| 11b | C++ unchecked `std::get_if` | `auto *v = std::get_if<int>(&var); *v = 42;` | `unchecked-get-if-result` | — | OSS only (unchanged) | High — nullptr return on type mismatch is well-defined | No — language construct, not a named function | `unchecked-get-if-result` |
| 12 | C++ iterator `find()` result not checked | `auto it = m.find(k); return it->second;` | `unchecked-map-find-result` | `unchecked-map-find-taint` | Both (unchanged) | High — dereferencing `end()` is always UB | No — fixed stdlib names | `unchecked-map-find-result` + `unchecked-map-find-taint` |
| 13 | Uninitialized out-parameter (CWE-457) | `int *out; get_val(&out); printf("%d", *out);` | — | `uninitialized-out-param-taint` | Pro only (partial — return-code sanitizer required, unchanged) | Low — partial coverage; return-code check sanitizer may miss non-standard error conventions | No — dataflow, not function-name driven | `uninitialized-out-param-taint` |
| 14 | `strtok`/`strtok_r`/`strsep` exhaustion | `while(1) { use(tok); tok = strtok(NULL, ","); }` | `strtok-loop-without-null-check` | `strtok-result-null-check-taint` | Both (unchanged) | High (OSS) / Medium (taint — may flag intentional sentinel loops) | No — fixed stdlib names | `strtok-loop-without-null-check` + `strtok-result-null-check-taint` |




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




