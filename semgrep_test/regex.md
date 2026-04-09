From claude opus 4.5: for completeness you should add $SINK(..., $X) to cover cases explicitly:                                                                                                                                                          

**...**

```
  pattern-sinks:                                                                                                                                                                                                                                           
    - pattern: $SINK($X)              # only argument                                                                                                                                                                                                      
    - pattern: $SINK($X, ...)         # first argument                                                                                                                                                                                                     
    - pattern: $SINK(..., $X)         # last argument                                                                                                                                                                                                      
    - pattern: $SINK(..., $X, ...)    # middle argument
```

It is wrong, Claude overcomplicated it:
```
  pattern-sinks:                                                                                                                                                                                                                                           
    - pattern: $SINK($X)              # only argument                                                                                                                                                                                                      
    - pattern: $SINK($X, ...)         # first argument ---> cover all argument                                                                                                                                                                                                    
    - pattern: $SINK(..., $X)         # last argument ---> cover all argument                                                                                                                                                                                                       
    - pattern: $SINK(..., $X, ...)    # middle argument ---> cover all argument 
```

Rule file:
```
rules:
  - id: untitled_rule
    patterns:
      - pattern-either:
          # - pattern: $SINK($X)              # only argument
          # - pattern: $SINK($X, ...)         # all argument
          # - pattern: $SINK(..., $X)         # all argument
          # - pattern: $SINK(..., $X, ...)    # all argument
    message: Semgrep found a match
    languages: [cpp]
    severity: WARNING
```

Test file:
```
foo(x);
foo(x, a, b);
foo(a, b, x);
foo(a, x, b);
```

Don't miss **;**
```
pattern: $SINK(..., $X, ...);
```
