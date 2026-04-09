Test: 
1. focus-metavariable: $X
- 1.1 pattern without focus-metavariable → taints the entire call expression
  ```
  # Pattern 2
  - patterns:
      - pattern: $FUNC(...)
      - metavariable-regex:
          metavariable: $FUNC
          regex: '^(X509_get_issuer_name|...)$'
    ```
    Semgrep taints the return value of the call — the whole expression `X509_get_issuer_name(ccert)`. That expression flows directly into `X509_NAME_oneline(...)` as an argument → sink fires: `X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024);` ✓

- 1.2 pattern with focus-metavariable on wrong/undefined/unbound object  

```
    pattern-sources:
    # catches: X509_NAME *name = X509_get_issuer_name(cert); (for variable tracking + sanitizer support)
    - patterns:
        - pattern: $TYPE *$X = $FUNC(...);
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X
    # catches: X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024); (inline, no assignment)
    - patterns:
        - pattern: $FUNC(...)
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X

```

  When focus-metavariable references an unbound metavariable, Semgrep has no expression to focus the taint on — this pattern silently produces zero taint. The effect is the same as deleting this pattern.
```
# Pattern 2 — $X is UNDEFINED here 
  - patterns:                                                                                                                                                                                                             
      - pattern: $FUNC(...)          # only $FUNC exists                                                                                                                                                                  
      - metavariable-regex:                                                                                                                                                                                               
          metavariable: $FUNC                                                                                                                                                                                             
          regex: '^(X509_get_issuer_name|X509_get_subject_name)$'                                                                                                                                                         
      - focus-metavariable: $X       # $X is unbound — nothing to focus on  
```
- 1.3 pattern with focus-metavariable on correct/bound object
```  
  # Pattern 1 — $X IS defined                                                                                                                                                                                             
  - patterns:                                                                                                                                                                                                             
      - pattern: $TYPE *$X = $FUNC(...)   # $X bound here as the LHS variable
      - ...                                                                                                                                                                                                               
      - focus-metavariable: $X            # valid — focuses taint on the variable
```


```
    pattern-sources:
    # catches: X509_NAME *name = X509_get_issuer_name(cert); (for variable tracking + sanitizer support)
    - patterns:
        - pattern: $TYPE *$X = $FUNC(...);
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X
    # catches: X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024); (inline, no assignment)
    - patterns:
        - pattern: $FUNC(...)
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $FUNC

```


        
2. side affect of broad sink function pattern



**Test file:**
```cpp
// Test 1 ============================================================================
void badcode(X509 *cert) 
{
    // ruleid: c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
    X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024);
    pan_debug("Client cert issuer is %s\n", buf);
    const char* p1 = strstr(buf, "/CN=");
    if (p1) {
        p1 += sizeof("/CN=") - 1;
        char* p2 = (char *)strstr(p1, "/");
        if (p2) {
            *p2 = '\0';
        }
    }
}

//Test 2: 
void good_name_checked_in_callee(X509 *cert)
{
    X509_NAME *name = X509_get_subject_name(cert);
    sink_name_checked(name);           // callee guards before use — ok
}

static void sink_name_checked(X509_NAME *name)
{
  if (!name)
   return;
   
  char buf[256];
  // c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
  X509_NAME_oneline(name, buf, sizeof(buf));
}

//Test 3  ============================================================================ 
void good_name_checked_in_caller(X509 *cert)
{

    X509_NAME *name = X509_get_issuer_name(cert);
    if (!name)
        return;
    
    sink_name(name);  // sanitized; sink_name not flagged here
}

static void sink_name(X509_NAME *name)
{
    char buf[256];
    // ok: c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
    X509_NAME_oneline(name, buf, sizeof(buf));
}

```


**Case 1: assigned**
To make the sanitizers work, we have to focus on $X Semgrep's focus-metavariable can only focus on metavariables explicitly bound in the pattern clause. 

**Rule1:**
**Run this rule against the test code, failed on Test 1, passed on Test 2 and Test 3. Because the source pattern does not cover inline call** 

```
rules:
  - id: c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
    mode: taint
    message: >
      Value from `$SOURCE` flows into `$SINK` without a NULL check across function or
      file boundaries. The OpenSSL source function can return NULL; passing it unchecked
      causes undefined behavior inside the callee.
    severity: HIGH
    languages: [c, cpp]
    options:
      interfile: true
    metadata:
      category: security
      cwe: "CWE-476: NULL Pointer Dereference"
      owasp: "A09:2004 - Denial of Service"
      technology:
        - c
        - Null-pointer dereference
      confidence: MEDIUM
      likelihood: HIGH
      impact: HIGH
      subcategory:
        - vuln
      references:
        - https://cwe.mitre.org/data/definitions/476.html
      note: >
        Companion to c.openssl.null-pointer-unchecked-nullable-pointer-use (search mode).
        That rule covers same-scope flows. This rule covers cross-function and cross-file flows.
        Sinks are constrained to known-dangerous OpenSSL API functions confirmed from triage
        of same-scope findings — prevents FP explosion from broad taint fan-out.
        Do NOT run both rules without deduplicating by file+line.
    pattern-sources:
      - patterns:
          - pattern: $TYPE *$X = $FUNC(...);
          - metavariable-regex:
              metavariable: $FUNC
              regex: '^(X509_get_issuer_name|X509_get_subject_name|X509_get_pubkey|X509_get0_pubkey|X509_get_ext_d2i|PEM_read_bio_X509|PEM_read_bio_X509_CRL|PEM_read_bio_X509_REQ|d2i_X509_bio|BIO_new|BIO_new_mem_buf|BIO_new_file|BIO_new_fp|BIO_new_ssl|BIO_new_connect|EVP_get_digestbyname|EVP_get_digestbynid|EVP_get_cipherbyname|EVP_MD_CTX_new|EVP_CIPHER_CTX_new|EVP_PKEY_CTX_new|EVP_PKEY_CTX_new_id|EVP_MD_fetch|EVP_CIPHER_fetch|PEM_read_bio_PrivateKey|PEM_read_bio_PUBKEY|PEM_read_bio_RSAPrivateKey|PEM_read_bio_ECPrivateKey|d2i_AutoPrivateKey|d2i_PrivateKey_bio|SSL_CTX_new|SSL_new|SSL_get_peer_certificate|SSL_get_session|EC_KEY_new_by_curve_name|EC_KEY_new|RSA_new|BN_new|BN_dup)$'
          - focus-metavariable: $X
    pattern-sanitizers:
      # braced forms
      - pattern: if (!$X) { ... }
      - pattern: if ($X == NULL) { ... }
      - pattern: if (NULL == $X) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if (NULL != $X) { ... }
      - pattern: if ($X) { ... }
      - pattern: if (!$X) return;
      - pattern: if ($X == NULL) return;
      - pattern: if (NULL == $X) return;
      - pattern: if (!$X) break;
      - pattern: if ($X == NULL) break;
    pattern-sinks:
      - pattern: $FUNC(..., $X, ...)
      - pattern: $X->$FIELD
      - pattern: "*$X"
```



**Case2: inline call**
if we change the source pattern to "$OUTER(...,$FUNC(...),...);",   
$X is never bound — $FUNC(...) is a call expression, but its return value is not captured into any named metavariable like $X.    
Semgrep has no way to know $X means "the return value of $FUNC(...)".                                                           
                                                                                                                                    
The only way to bind a return value to $X is with an assignment:                                                                  
   
  - pattern: $X = $FUNC(...);   # $X is now bound to the return value                                                               
                                                                                                                                    
  But your bad code never does that — the return value is passed inline directly to $OUTER
  , so there's no $X to bind.               
                                                                                                                                    
  Why the outer pattern makes it worse:                                                                                              
                                                                                                                                  
  By wrapping in $OUTER(...), you're also making the source match the whole outer call expression. Even if taint propagation worked,
   what gets marked tainted is the return of $OUTER (i.e., X509_NAME_oneline(...)), not the inner NULL-returning $FUNC(...).  

  The real fix                                                                                                                    

  Drop the outer wrapper and focus-metavariable entirely:                                                                           
   
  pattern-sources:                                                                                                                  
    - patterns:                                                                                                                   
        - pattern: $FUNC(...)
        - metavariable-regex:                                                                                                       
            metavariable: $FUNC
            regex: ^(X509_get_subject_name|BIO_new|X509_get_issuer_name)$    

  In Semgrep taint mode, a source pattern with no focus-metavariable marks the matched expression itself — i.e., the return value of
   $FUNC(...) — as tainted. That taint then flows into $OUTER(...) as an argument, hits your sink $SINK(...,$X,...), and the rule   
  fires.                                                                                                                            

  **Rule2:**

Added inline call pattern as the source pattern 2:
**Run this rule against the test code, Test 1 passed, Test2 and Test3 failed. ** 


```
rules:
  - id: c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
    mode: taint
    message: |
      test.
    severity: HIGH
    languages:
      - c
      - cpp
    options:
      interfile: true
    metadata:
      category: security
      cwe: "CWE-476: NULL Pointer Dereference"
      owasp: A09:2004 - Denial of Service
      technology:
        - c
        - Null-pointer dereference
      confidence: MEDIUM
      likelihood: HIGH
      impact: HIGH
      subcategory:
        - vuln
      references:
        - https://cwe.mitre.org/data/definitions/476.html
    pattern-sources:
    # catches: X509_NAME *name = X509_get_issuer_name(cert); (for variable tracking + sanitizer support)
    - patterns:
        - pattern: $TYPE *$X = $FUNC(...);
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X
    # catches: X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024); (inline, no assignment)
    - patterns:
        - pattern: $FUNC(...)
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
    pattern-sanitizers:
      - pattern: if (!$X) { ... }
      - pattern: if ($X == NULL) { ... }
      - pattern: if (NULL == $X) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if (NULL != $X) { ... }
      - pattern: if ($X) { ... }
      - pattern: if (!$X) return;
      - pattern: if ($X == NULL) return;
      - pattern: if (NULL == $X) return;
      - pattern: if (!$X) break;
      - pattern: if ($X == NULL) break;
    pattern-sinks:
      - pattern: $SINK(...,$X, ...)
      - pattern: $X->$FIELD
      - pattern: "*$X"
```
            
  **Rule3:**

Added focus-metavariable: $X to the source pattern 2:
**Run this rule against the test code, Test 1 failed, Test2 and Test3 passed. Because the source pattern does not cover inline call** 

```
rules:
  - id: c.openssl.null-pointer-unchecked-nullable-pointer-use-interfile
    mode: taint
    message: |
      test.
    severity: HIGH
    languages:
      - c
      - cpp
    options:
      interfile: true
    metadata:
      category: security
      cwe: "CWE-476: NULL Pointer Dereference"
      owasp: A09:2004 - Denial of Service
      technology:
        - c
        - Null-pointer dereference
      confidence: MEDIUM
      likelihood: HIGH
      impact: HIGH
      subcategory:
        - vuln
      references:
        - https://cwe.mitre.org/data/definitions/476.html
    pattern-sources:
    # catches: X509_NAME *name = X509_get_issuer_name(cert); (for variable tracking + sanitizer support)
    - patterns:
        - pattern: $TYPE *$X = $FUNC(...);
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X
    # catches: X509_NAME_oneline(X509_get_issuer_name(ccert), buf, 1024); (inline, no assignment)
    - patterns:
        - pattern: $FUNC(...)
        - metavariable-regex:
            metavariable: $FUNC
            regex: '^(X509_get_issuer_name|X509_get_subject_name)$'
        - focus-metavariable: $X
    pattern-sanitizers:
      - pattern: if (!$X) { ... }
      - pattern: if ($X == NULL) { ... }
      - pattern: if (NULL == $X) { ... }
      - pattern: if ($X != NULL) { ... }
      - pattern: if (NULL != $X) { ... }
      - pattern: if ($X) { ... }
      - pattern: if (!$X) return;
      - pattern: if ($X == NULL) return;
      - pattern: if (NULL == $X) return;
      - pattern: if (!$X) break;
      - pattern: if ($X == NULL) break;
    pattern-sinks:
      - pattern: $SINK(...,$X, ...)
      - pattern: $X->$FIELD
      - pattern: "*$X"
```


                                                                                                                             
