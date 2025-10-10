## $_FILES[$fileName]['tmp_name']
The fundamental issue is that tmp_name has an implicit security contract in PHP - it should always be server-controlled and safe to use without additional validation.

```php
$filePath = realpath($_POST[$fileName]);

if (strpos($filePath, "/opt/smth/tmp/") !== 0) {
    Debug::logToFile("Detected a malicious access attempt to access a file at location ${filePath}. Will ignore");
    return;
}

$_FILES[$fileName] = array(
    'size' => $_POST[$size], 
    'tmp_name' => $filePath,  // <-- TAINTED!
    'error' => 0, 
    'type' => $_POST[$contentType], 
    'name' => $_POST[$clientFileName]
);
```
`tmp_name` is now tainted with user-controlled input!

Normally, `$_FILES['field']['tmp_name']` contains a server-generated temporary file path that PHP creates during upload (like /tmp/phpXXXXXX)
Here, `tmp_name` is being overwritten with `$_POST[$fileName]` after passing through realpath()
Even though there's a path validation check (strpos($filePath, "/opt/smth/tmp/") !== 0), this is still user-controlled data.

**Key Security Properties of tmp_name**
1. Server-Generated Path
// Normal tmp_name examples:
'/tmp/phpABC123'     // Linux/Unix
'C:\Windows\Temp\phpDEF456'  // Windows

PHP generates these paths using secure random names
Always in the system's designated temp directory
Never user-controllable

2. Automatic Cleanup
PHP automatically deletes these temp files at request end
Files are isolated per request
No persistence beyond script execution

3. Trust Boundary
// Safe operations - tmp_name is trusted
$content = file_get_contents($_FILES['upload']['tmp_name']); // Safe
move_uploaded_file($_FILES['upload']['tmp_name'], $dest);    // Safe


**Security Violation**
Breaks the trust model: tmp_name should never be user-controlled
Path injection: User can specify any file path (within /opt/smth/tmp/)
Bypasses PHP's security: No automatic cleanup, no isolation

