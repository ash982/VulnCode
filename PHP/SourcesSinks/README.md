## Possible Sources (Entry Points for Untrusted Data)
Sources are places where user-controllable data enters the application. Any variable that an attacker can influence is a potential source.

**Several superglobals and server-side elements contain data that can be directly or indirectly controlled by a user.** 
| Source Category	| PHP Superglobal/Method |	Description
| :--- | :--- | :--- |
| HTTP Request Data |	$_GET	| URL query parameters. e.g. `$_GET['name']` |
| | `$_POST` |	Data from a submitted HTML form body. e.g. `$_POST['username']`|
| | `$_COOKIE` |	Values stored in HTTP cookies. e.g. `$_COOKIE['username']`|
| | `$_REQUEST`	| Combined contents of `$_GET`, `$_POST`, and `$_COOKIE`. e.g. `$_REQUEST['email']` |
| | `$_FILES` |	Information about uploaded files (e.g., file name, contents). |
| | `getallheaders() / `$_SERVER` |	HTTP request headers (e.g., `User-Agent`, `Referer`, `Host`). |
| File Upload via HTTP POST | `$_FILES` |	holds information about files uploaded |
| Som server info |	`$_SERVER` |	the HTTP headers sent by the client. |
| Database Input |	Data read from a database that originated from a user. | User-supplied content stored in tables and later retrieved.|
| File I/O	| Data read from files or external resources. |	Reading configuration files, log files, or remote resources via `file_get_contents()`.|
| Environment |	`$_ENV` / `getenv()` |	Environment variables. |


## Potential security issues with `$_REQUEST`: 
By default, `$_REQUEST` contains the contents of `$_GET`, `$_POST`, and `$_COOKIE`.  

It is generally not recommended to use `$_REQUEST` because its non-explicit nature can lead to security vulnerabilities like Cross-Site Request Forgery (CSRF). For instance, an unexpected cookie or URL parameter could override a POST value.
Best practice: For better security and code clarity, use `$_GET` or `$_POST` directly to explicitly state where the data is expected to come from.
'bad-csrf.php'  

`$_FILES`  
What it is: A superglobal associative array that holds information about files uploaded via an HTTP POST request.   
**You cannot get the contents of $_FILES from `$_REQUEST`. File upload data is handled separately and stored exclusively in the $_FILES superglobal. 
$_GET, $_POST, and $_COOKIE contain simple key-value pairs of strings. File uploads, however, involve transferring binary data and require special processing by the PHP engine.**   
How it is user-controlled: A user directly supplies the file and its metadata (name, size, type) through a file upload form.  
Security risks: An attacker could upload a malicious file (e.g., a PHP script disguised as an image) to gain control of the server if the application does not properly validate the file type and contents.    

`$_SERVER`  
What it is: A superglobal that contains server and execution environment information, including many HTTP headers sent by the client.  
This is a comprehensive list of common `$_SERVER` values, highlighting which ones are controlled by the client and are therefore untrustworthy without proper validation and sanitization.   
Not all web servers populate every one of these variables, so some may be empty depending on the environment.  

How it is user-controlled: Although primarily server-side data, many values are set by the client and are therefore user-controlled. Examples include:  
**`$_SERVER` Client/User-controlled values (Untrusted)**  
These values are set by the client and must always be treated as untrusted input. Improper use can lead to XSS, CSRF, and other vulnerabilities.   

| `$_SERVER`	| Description |
| :--- | :--- |
| `$_SERVER['HTTP_ACCEPT']` | Acceptable content types from the client. | 
| `$_SERVER['HTTP_ACCEPT_CHARSET']` | Character sets acceptable by the client. | 
| `$_SERVER['HTTP_ACCEPT_ENCODING']` | Encoding schemes acceptable by the client. | 
| `$_SERVER['HTTP_ACCEPT_LANGUAGE']` | Languages acceptable by the client. | 
| `$_SERVER['HTTP_CACHE_CONTROL']` | Cache control headers. | 
| `$_SERVER['HTTP_CONNECTION']` | Connection type. | 
| `$_SERVER['HTTP_COOKIE']` | The raw cookie string sent from the client. The parsed version is in `$_COOKIE`. | 
| `$_SERVER['HTTP_HOST']` | The content of the Host header sent by the client, which can be manipulated to perform cache poisoning or other attacks.. Can be used for "Host Header Injection" attacks.  | 
| `$_SERVER['HTTP_REFERER']` | The previous page visited. Easily spoofed. | 
| `$_SERVER['HTTP_USER_AGENT']` | The user agent (browser) string. Easily spoofed. |
| `$_SERVER['HTTP_X_FORWARDED_FOR']` | A common non-standard header used by proxies and load balancers to reveal the originating IP address of a client. This, along with other `X-Forwarded-*` headers like `HTTP_X_DEBUG_CUSTOM`, can be forged. |
| `$_SERVER['PATH_INFO']` | Path information from the URL. An attacker can append arbitrary data. | 
| `$_SERVER['PHP_SELF']` | The current script's filename. An attacker can inject XSS by appending a malicious string to the URL, which is then reflected in a form's action attribute. The script filename relative to the document root. This is dangerous because an attacker can append a string to the URL, which is then reflected in PHP_SELF, leading to XSS if not properly escaped. | 
| `$_SERVER['QUERY_STRING']` | The query string from the URL. This is the source for `$_GET` variables. | 
| `$_SERVER['REQUEST_URI']` | The URI used to access the page. Contains the user-supplied path and query string and can be tainted. | 
| `$_SERVER['REMOTE_HOST']` | The hostname of the client. This relies on reverse DNS lookups and may be spoofed. | 
| `$_SERVER['AUTH_TYPE']`, `$_SERVER['PHP_AUTH_USER']`, `$_SERVER['PHP_AUTH_PW']` | Variables related to HTTP authentication. The web server processes the `Authorization` header | 
| `$_SERVER['argv']`, `$_SERVER['argc']` | Relevant for command-line scripts, but can be controlled by user arguments in that context (not from http clinet) |   

**`$_SERVER['HTTP_*']`: Any value beginning with HTTP_ is directly from an HTTP header and should be considered user-controlled.**    

**`$_SERVER` Server-controlled values (Generally safe)**  
These values are set by the server and are considered generally trustworthy, but misconfiguration or a compromised server could change this.   
| `$_SERVER`	| Value |
| :--- | :--- |
| `$_SERVER['DOCUMENT_ROOT']`| The document root directory under which the current script is executing.
| `$_SERVER['GATEWAY_INTERFACE']`| The version of the Common Gateway Interface (CGI) the server is using.
| `$_SERVER['SERVER_ADDR']`| The IP address of the server executing the script.
| `$_SERVER['SERVER_NAME']`| The name of the host server. This can be overridden by a user-supplied HTTP_HOST header depending on server configuration.
| `$_SERVER['SERVER_PORT']`| The port on the server machine being used.
| `$_SERVER['SERVER_PROTOCOL']`| The name and revision of the protocol.
| `$_SERVER['SERVER_SIGNATURE']`| The server version and virtual host name, if enabled.
| `$_SERVER['SERVER_SOFTWARE']`| The server identification string.
| `$_SERVER['SCRIPT_FILENAME']`| The absolute pathname of the currently executing script.
| `$_SERVER['REMOTE_ADDR']`| The IP address from which the user is viewing the current page. While the client can't forge this value directly (it is part of the TCP/IP handshake), it can be an intermediary proxy address rather than the end-user's address.
| `$_SERVER['REQUEST_TIME']`| The timestamp of the start of the request. 

**Best practices**  
1. Always escape output: Any `$_SERVER` value that is printed back to the browser should be escaped using `htmlspecialchars()` to prevent XSS attacks.  
2. Avoid PHP_SELF: Use `$_SERVER['SCRIPT_NAME']` instead of `$_SERVER['PHP_SELF']` when generating links or form actions to avoid XSS vulnerabilities.  
3. Validate input: Never trust any data coming from the client. Perform strict validation on values like `HTTP_HOST` or `REQUEST_URI` if they are used for critical logic.  
4. Assume everything is tainted: When in doubt, assume a value is user-controlled and treat it accordingly.   

`$_SESSION`  
What it is: A superglobal that stores data for the duration of a user's session. The data itself is stored on the server, not the client.  
How it is user-controlled: While a user cannot directly alter session variables, the values they contain can come from user-controlled input (e.g., a form field). Additionally, attackers can use "session hijacking" or "session fixation" to manipulate a victim's session by stealing or setting a session ID cookie.  
Security risks: **If you assign a session variable directly from an unfiltered $_GET or $_POST value**, the session becomes susceptible to malicious input.  

`$_ENV`  
What it is: A superglobal array of variables passed to the script from the environment in which the PHP parser is running.  
How it is user-controlled: In certain server configurations, attackers may be able to manipulate environment variables, such as the PATH or temporary file locations, to execute malicious code.  
Security risks: While uncommon for web requests, relying on environment variables that can be modified by a less-privileged user on a shared system is a risk.  

## Dangerous Sinks (Functions that Execute or Interpret Data)  
Sinks are functions where untrusted data is processed in a sensitive context, leading to injection if the data isn't properly sanitized or validated.  

**A. Code Execution Sinks (Remote Code Execution - RCE)**  
These functions can directly execute attacker-controlled strings as PHP code or OS commands.  
| Sink Function	| Injection Type | Description |
| :--- | :--- | :--- |
| `eval()` | PHP Code Injection | Executes a string as PHP code. Highly dangerous.
| `assert()` | PHP Code Injection | Executes a string as PHP code (often used for debugging).
| `preg_replace()` (with `/e` modifier - deprecated/removed) | PHP Code Injection | The replacement string is evaluated as PHP code.
| `unserialize()` | Object Injection | Deserializes user input, which can trigger methods like `__destruct()` in malicious objects, leading to RCE (known as PHP Object Injection).
| `create_function()` (deprecated/removed) | PHP Code Injection | Creates an anonymous function from a string.
| `shell_exec(), exec(), system(), passthru(), popen(), proc_open()` | OS Command Injection | Executes operating system commands.

**B. File Inclusion Sinks (Local/Remote File Inclusion - LFI/RFI)**  
These functions dynamically load files, which an attacker can abuse to include malicious scripts.  
| Sink Function	| Injection Type | Description |
| :--- | :--- | :--- |
| `include(), include_once(), require(), require_once()` | File Inclusion (LFI/RFI) |	Includes and evaluates the specified file. RFI is possible if allow_url_include is enabled.
| `file_get_contents(), readfile(), fopen()` |	Arbitrary File Read |	While not direct code execution, these can be used to read sensitive files (e.g., `/etc/passwd` or source code).

**C. Output Sinks (Cross-Site Scripting - XSS)**  
These functions output data directly to an HTML page without proper encoding, allowing for HTML/JavaScript injection.  

| Sink Function	| Injection Type | Description |
| :--- | :--- | :--- |
| echo, print, print_r, printf, vprintf	| XSS |	Output functions. If they output un-sanitized user data to HTML, XSS is possible.


**D. Database Sinks (SQL Injection)**  
These functions execute database queries constructed with un-sanitized user input.  

| Sink Function	| Injection Type | Description |
| :--- | :--- | :--- |
| `mysql_query(), mysqli_query(), PDO::exec()`	| SQL Injection |	Executes a database query string constructed from user input.

## Code Injection vs. Command Injection  
The fundamental difference between Code Injection and Command Injection lies in the **execution environment** and the language being interpreted.  
| Feature |	Code Injection |	Command Injection
| :--- | :--- | :--- |
| Execution Context |	The application's runtime environment or programming language interpreter. |	The underlying operating system (OS) shell (e.g., Bash, cmd.exe).
| Language Injected |	The application's source language (e.g., **PHP, Python, JavaScript, Java, SQL**). |	OS shell commands (e.g., `ls, cat, whoami, ping`).
| Mechanism |	The application's code uses an unsafe function (the sink) to dynamically execute a string as part of its own programming logic. |	The application's code passes unsanitized user input as an argument to a function that executes an OS command.
| Scope of Impact |	Primarily limited to the **functionality and permissions of the application's language** within its environment. |	Can impact the entire **operating system** and everything the user running the application has access to.

**1. Code Injection (Targeting the Application)**  
Code injection is the general term for attacks where an attacker inserts code that is **interpreted and executed by the application itself**. The malicious code is written in the application's language (or a language the application uses, like **SQL or JavaScript**).  

Example (PHP Code Injection)  
An application uses the dangerous `eval()` function to execute a string as PHP code:  
```php
// PHP Code (Vulnerable Sink)
eval("echo 'User input: ' . $_GET['data'];");
```

Attack Payload: `data=1; phpinfo()`  
Code Executed: `echo 'User input: 1; phpinfo()';`  

The attacker's payload (`phpinfo()`) is interpreted and executed by the PHP interpreter. The attacker is limited by what the PHP language can do.  

**2. Command Injection (Targeting the Operating System)**  
Command injection (often called OS Command Injection or Shell Injection) is a type of injection where an attacker inserts commands that are executed by the host operating system's shell.  

Example (PHP with OS Command Injection)  
An application uses the dangerous `system()` function to execute an OS command based on user input:  
```php
// PHP Code (Vulnerable Sink)
system("ls -l /var/www/uploads/ | grep " . $_GET['filename']);
```

Attack Payload: `filename=image.jpg; whoami`  
Shell Command Executed: `ls -l /var/www/uploads/ | grep image.jpg; whoami`  

The special character `;` (a shell command separator) is used to tell the shell to end the first command (`grep...`) and execute a second, arbitrary command (`whoami`). The attacker is limited by what the underlying OS shell can execute.  

**Key Takeaway**  
A successful Code Injection attack gives the attacker **control over the application's language interpreter (e.g., executing a PHP function)**.  

A successful Command Injection attack gives the attacker control over the **server's operating system shell** (e.g., executing a Linux command).  

**While Code Injection can sometimes be leveraged to achieve Command Injection (e.g., by using an injected PHP function like system() or exec()), they are distinct vulnerabilities based on where the malicious input is executed.**  


## Prevention strategies  
Preventing code injection relies on the principle of never trusting user input and rigorously separating data from code. **Relying solely on escaping is often insufficient and can be error-prone;** the best defense is using secure, built-in APIs designed to handle data safely.  

Here is a breakdown of the primary prevention strategies, including specific PHP methods.  
**1. Prioritize Safe APIs (The Best Defense) 🛡️**  

Instead of trying to clean or "escape" every special character manually, use functions that treat user input as inert data, not executable code.  

**A. Preventing SQL Injection**  

Use Parameterized Queries (Prepared Statements): This is the gold standard. The database driver handles the user data separately from the SQL query structure, ensuring user input is always treated as data.  

```php
// Safe PDO Example
$stmt = $pdo->prepare('SELECT * FROM users WHERE username = :user');
$stmt->execute([':user' => $_POST['username']]);
```

**B. Preventing Command Injection**  

1. Avoid Calling Shell Commands: The most secure approach is to use native PHP functions instead of calling external programs.  

Example1:
Instead of: `system('rm ' . $file);`  
Use: `unlink($file);`  

Example2: In PHP, any string enclosed in **backticks** is treated as a shell command and is executed immediately by the operating system. This is a built-in feature of the language.  
Execution: The PHP interpreter takes the entire string inside the backticks (ls -l $filename), passes it to the underlying shell (like Bash or Zsh), and waits for it to finish.  
Assignment: The output (stdout) of that shell command (the file listing, in this case) is then captured and assigned to the variable $file_listing.  
```php
    // 1. Source: Get unsanitized user input (e.g., from a URL parameter like ?file=...)
    $filename = $_GET['file'];

    // 2. Sink: Execute the shell command using the backtick operator
    // An attacker can set ?file=; cat /etc/passwd
    // The resulting command will be: ls -l ; cat /etc/passwd
    // ruleid: panw.php.backend.command-injection
    $file_listing = `ls -l $filename`;
```
2. If you MUST use a shell command: Use built-in PHP functions to properly escape arguments for the shell.  
    `escapeshellcmd()`: Escapes the entire command string (use this if the user controls the command).  
    `escapeshellarg()`: Escapes a single argument to a command (use this if the user controls a parameter to a fixed command).  
```php
// Safe Command Injection Example
$file = escapeshellarg($_GET['filename']); 
// The command itself is fixed, only the argument is user-controlled
system('ls -l ' . $file); 
```



**C. Preventing PHP Code Execution (e.g., eval(), include())**  
1. Do Not Use Dangerous Sinks: Functions like eval(), assert(), and create_function() should almost always be avoided in production code as they are the primary enablers of PHP Code Injection.  

2. File Inclusion: To prevent Local File Inclusion (LFI), use a whitelist of allowed filenames or prepend a fixed, safe path and ensure the user input only contains the base file name.  

```php
// Safe File Inclusion Example
$page = $_GET['page'];
// Whitelist check
if (!in_array($page, ['home.php', 'about.php', 'contact.php'])) {
    die("Invalid page selected.");
}
// Fixed base path ensures user cannot navigate directories
include('pages/' . $page);
```

## 2. Contextual Escaping (For Output) 🎨  
Escaping is primarily used to prevent Cross-Site Scripting (XSS), which is a form of injection where malicious code (usually JavaScript) is executed in the user's browser. The key is to escape data based on where it will be placed in the HTML document.  

**A. Escaping for HTML Content**  
Use `htmlspecialchars()` to convert special characters into their HTML entities. This makes sure the browser treats characters like < and > as text, not as HTML tags.  

Original Character	HTML Entity  
```
<	&lt;
>	&gt;
&	&amp;
"	&quot;
```

```php
<?php
$user_comment = $_POST['comment'];
// Vulnerable: user could enter <script>alert(1)</script>
// echo $user_comment; 

// Safe: converts < to &lt; and > to &gt;
echo htmlspecialchars($user_comment, ENT_QUOTES, 'UTF-8');
?>
```

**B. Escaping for HTML Attributes**  
If placing user input inside an HTML tag attribute, use htmlspecialchars().  
```php
// Safe for XSS in attributes
echo '<input type="text" value="' . htmlspecialchars($user_input) . '">';
```

**C. Escaping for JavaScript**  
If you need to put user input inside a JavaScript block, use json_encode() to securely escape the string, ensuring it is a valid JavaScript string literal.  
```php
// Safe for JavaScript
echo "<script>";
// The user input is safely encoded by json_encode()
echo "var username = " . json_encode($user_input) . ";"; 
echo "</script>";
```

## 3. Input Validation (Defense in Depth) 📥  
While validation doesn't prevent injection (that's the job of safe sinks and escaping), it does limit the type of data an attacker can send, making exploitation more difficult.  

1. Whitelisting: Accept only expected characters (e.g., alphanumeric). This is the strongest validation.  

2. Type Casting: Convert input to the expected type (e.g., `$id = (int)$_GET['id'];`). This automatically neutralizes all non-numeric characters for simple values.  

3. Filtering: Use PHP's built-in `filter_var()` family of functions for powerful, standardized validation and sanitization.  
`filter_var(mixed $value, int $filter = FILTER_DEFAULT, array|int $options = 0): mixed`  

**Common filter types**  
a. Validation filters  
Validation filters check if a value conforms to a specific format and return the original value on success or FALSE on failure. Examples include:   
`FILTER_VALIDATE_EMAIL`: Validates an email address.  
`FILTER_VALIDATE_INT`: Validates an integer.  
`FILTER_VALIDATE_URL`: Validates a URL.  
`FILTER_VALIDATE_IP`: Validates an IP address.   
You can find examples of how to use these validation filters in the referenced web document.   

b. Sanitization filters  
Sanitization filters clean data by removing or encoding potentially malicious characters for safe use. Some sanitization filters are:   
`FILTER_SANITIZE_STRING`: (Deprecated in PHP 7.3, removed in PHP 8.0) Used to strip tags and special characters. Instead, htmlspecialchars() or `strip_tags()` are recommended, or use FILTER_SANITIZE_SPECIAL_CHARS with the FILTER_FLAG_STRIP_LOW flag.  
`FILTER_SANITIZE_EMAIL`: Removes illegal characters from an email address.  
`FILTER_SANITIZE_URL`: Removes illegal characters from a URL.  
`FILTER_SANITIZE_NUMBER_INT`: Removes all characters except digits, plus, and minus signs.  

```php
// Validating an email address
$email = filter_var($_POST['email'], FILTER_VALIDATE_EMAIL);
if ($email === false) {
    die("Invalid email format.");
}
```

```php
<?php
// Sanitizing a string
$html_input = "<h1>Hello, World!</h1> <script>alert('XSS');</script>";
$sanitized_string = filter_var($html_input, FILTER_SANITIZE_STRING); // Deprecated in PHP 8.1, use htmlspecialchars or strip_tags instead
echo $sanitized_string; // Output: Hello, World! alert('XSS');
?>
```

```php
<?php
//Validating an integer with range options
$age = "25";
$options = array(
    'options' => array(
        'min_range' => 18,
        'max_range' => 65
    )
);
if (filter_var($age, FILTER_VALIDATE_INT, $options)) {
    echo "Valid age.";
} else {
    echo "Invalid age.";
}
?>
```
