## Possible Sources (Entry Points for Untrusted Data)
Sources are places where user-controllable data enters the application. Any variable that an attacker can influence is a potential source.

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

It is generally not recommended to use $_REQUEST because its non-explicit nature can lead to security vulnerabilities like Cross-Site Request Forgery (CSRF). For instance, an unexpected cookie or URL parameter could override a POST value.
Best practice: For better security and code clarity, use $_GET or $_POST directly to explicitly state where the data is expected to come from.
'bad-csrf.php'

**Several other superglobals and server-side elements contain data that can be directly or indirectly controlled by a user.** 
`$_FILES`
What it is: A superglobal associative array that holds information about files uploaded via an HTTP POST request. 
**You cannot get the contents of $_FILES from `$_REQUEST`. File upload data is handled separately and stored exclusively in the $_FILES superglobal. 
$_GET, $_POST, and $_COOKIE contain simple key-value pairs of strings. File uploads, however, involve transferring binary data and require special processing by the PHP engine.**
How it is user-controlled: A user directly supplies the file and its metadata (name, size, type) through a file upload form.
Security risks: An attacker could upload a malicious file (e.g., a PHP script disguised as an image) to gain control of the server if the application does not properly validate the file type and 
contents.

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
| `$_SERVER['AUTH_TYPE']`, `$_SERVER['PHP_AUTH_USER']`, `$_SERVER['PHP_AUTH_PW']` | Variables related to HTTP authentication. | 
| `$_SERVER['argv']`, `$_SERVER['argc']` | Relevant for command-line scripts, but can be controlled by user arguments in that context.  | 

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
`// PHP Code (Vulnerable Sink)
eval("echo 'User input: ' . $_GET['data'];"); `

Attack Payload: `data=1; phpinfo()`
Code Executed: `echo 'User input: 1; phpinfo()';`

The attacker's payload (`phpinfo()`) is interpreted and executed by the PHP interpreter. The attacker is limited by what the PHP language can do.

**2. Command Injection (Targeting the Operating System)**
Command injection (often called OS Command Injection or Shell Injection) is a type of injection where an attacker inserts commands that are executed by the host operating system's shell.

Example (PHP with OS Command Injection)
An application uses the dangerous `system()` function to execute an OS command based on user input:
`// PHP Code (Vulnerable Sink)
system("ls -l /var/www/uploads/ | grep " . $_GET['filename']); `

Attack Payload: `filename=image.jpg; whoami`
Shell Command Executed: `ls -l /var/www/uploads/ | grep image.jpg; whoami`

The special character `;` (a shell command separator) is used to tell the shell to end the first command (`grep...`) and execute a second, arbitrary command (`whoami`). The attacker is limited by what the underlying OS shell can execute.

**Key Takeaway**
A successful Code Injection attack gives the attacker **control over the application's language interpreter (e.g., executing a PHP function)**.

A successful Command Injection attack gives the attacker control over the **server's operating system shell** (e.g., executing a Linux command).

**While Code Injection can sometimes be leveraged to achieve Command Injection (e.g., by using an injected PHP function like system() or exec()), they are distinct vulnerabilities based on where the malicious input is executed.**








