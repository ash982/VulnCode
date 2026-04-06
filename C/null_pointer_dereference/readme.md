**'return nullptr;' is not same as 'return NULL'**  
In C++11 and later, nullptr is preferred and safer:

  - nullptr — a typed null pointer constant (std::nullptr_t). Cannot be accidentally used as an integer.
  - NULL — typically defined as 0 or (void*)0. Can implicitly convert to int, causing ambiguity in overloaded functions.

  Example where they differ:

  void foo(int);
  void foo(char*);

  foo(NULL);    // Ambiguous or calls foo(int) — not what you want
  foo(nullptr); // Unambiguously calls foo(char*)

In C, nullptr doesn't exist (until C23). NULL is the standard null pointer constant there.  




