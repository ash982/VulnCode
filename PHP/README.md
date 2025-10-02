# Common Pitfalls and Bypass Techniques
## stripslashes and addslashes
**stripslashes**
stripslashes() only removes backslashes but doesn't sanitize HTML/JavaScript content, insufficient Input Sanitization.

**addslashes**
Here are the main techniques that demonstrate why addslashes() used in SQL query is insufficient protection:

**addslashes() only escapes these characters:**
```
Single quote (') → '
Double quote (") → "
Backslash () → \
NULL byte → \0
```

**1. Character Set Vulnerabilities**
When using multi-byte character sets (like GBK, Big5):

```php
// Vulnerable code
$input = addslashes($_GET['input']);
$query = "SELECT * FROM users WHERE name = '$input'";
```
Bypass:
Input: `%bf%27 OR 1=1 --`
After addslashes: `%bf%5c%27 OR 1=1 --`
In GBK charset: `%bf%5c becomes 縗 (single character)`
Result: `SELECT * FROM users WHERE name = '縗' OR 1=1 --'`

**2. Second-Order SQL Injection**
When escaped data is stored and later used without re-escaping:

```php
// First request - data gets stored with escaping
$name = addslashes("O\'Malley"); // Becomes O\'Malley in DB

// Later request - data retrieved and used without escaping
$stored_name = get_from_db(); // O'Malley (unescaped)
$query = "SELECT * FROM logs WHERE user = '$stored_name'"; // Vulnerable!
```
**3. Numeric Context Injection**
When injecting into numeric fields without quotes:

```php
$id = addslashes($_GET['id']); // addslashes has no effect on numbers
$query = "SELECT * FROM users WHERE id = $id"; // No quotes around $id
```
Bypass:
Input: `1 OR 1=1`
Query becomes: `SELECT * FROM users WHERE id = 1 OR 1=1`

**4. LIKE Clause Bypasses**
Using wildcards that aren't escaped by addslashes():

```php
$search = addslashes($_GET['search']);
$query = "SELECT * FROM products WHERE name LIKE '%$search%'";
```
Bypass:
Input: `%' UNION SELECT password FROM users WHERE '1'='1`
Works because `%` and `_` are not escaped by `addslashes()`

**5. Encoding Bypasses**
Using different encodings to bypass filtering:

URL encoding
%2527 → %27 → ' (after URL decode)

Unicode encoding
\u0027 → ' (in some contexts)

Hex encoding
0x27 → ' (in MySQL)

Real-World Example
Looking at your codebase, here's how an attack might work:

```php
// In the vulnerable insert_tdb function
$severity = $_POST['severity']; // No addslashes() applied!
$query = "insert into tdb (...) values (..., '$severity', ...)";
```

Attack payload:  
POST data: `severity=high', (SELECT password FROM admin_users LIMIT 1), 'fake`  

Resulting query:    
`INSERT INTO tdb (...) VALUES (..., 'high', (SELECT password FROM admin_users LIMIT 1), 'fake', ...)`


# Proper Prevention
Instead of trying to fix addslashes(), use these secure methods:  

1. Prepared Statements (Recommended)  
```php
$stmt = $conn->prepare("INSERT INTO tdb (title, severity) VALUES (?, ?)");
$stmt->bind_param("ss", $title, $severity);
$stmt->execute();
```  

2. Proper Escaping Functions  
```php
// Use database-specific escaping
$severity = mysqli_real_escape_string($conn, $_POST['severity']);

// Or PDO quote
$severity = $pdo->quote($_POST['severity']);
```

3. Input Validation  
```php
// Whitelist allowed values
$allowed_severities = ['critical', 'high', 'medium', 'low', 'informational'];
if (!in_array($_POST['severity'], $allowed_severities)) {
    die('Invalid severity');
}
```

The key takeaway is that addslashes() provides a false sense of security and should never be relied upon for SQL injection prevention. Always use parameterized queries or proper database-specific escaping functions.

## escapeshellcmd and escapeshellarg
escapeshellarg() vs. escapeshellcmd() at a glance
| Feature | escapeshellarg() | escapeshellcmd() |
| :--- | :--- | :--- |
| Purpose | Escapes a single argument to a command.	| Escapes metacharacters in the entire command string.
| Security | Safe for user-supplied arguments because it wraps them in quotes. | Can be unsafe for user-supplied arguments and can be bypassed for injection.
| Recommended use | For every individual argument from user input.	| Only for the command name if it must come from user input (very rare and risky).
| Output | Wraps the string in single quotes and escapes existing single quotes.| Prefixes special characters (#, &, ;, etc.) with a backslash.

**Best practices for executing shell commands**
1. Use escapeshellarg() for each argument derived from user input.
2. Define a static command name and never allow user input to control the executable.
3. Use **absolute paths** for executables to prevent the shell from using malicious path variables.
4. Consider not using shell execution at all if a native PHP function can achieve the same result. The less you interact with the system shell, the more secure your application will be.
5. Run commands with the least privilege possible by using a dedicated, sandboxed system user for your web application. 

