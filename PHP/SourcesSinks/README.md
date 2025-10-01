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
| Database Input |	Data read from a database that originated from a user. | User-supplied content stored in tables and later retrieved.|
| File I/O	| Data read from files or external resources. |	Reading configuration files, log files, or remote resources via `file_get_contents()`.|
| Environment |	`$_ENV` / `getenv()` |	Environment variables. |

In PHP, `$_GET`, `$_POST`, and `$_COOKIE` are superglobal associative arrays used to retrieve data passed to a script via different methods. 
`$_REQUEST` is another superglobal that, by default, contains the contents of the other three.

## Potential security issues with `$_REQUEST`: 
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
How it is user-controlled: Although primarily server-side data, many values are set by the client and are therefore user-controlled. Examples include:
`$_SERVER['HTTP_HOST']`: The Host header, which can be manipulated to perform cache poisoning or other attacks.
`$_SERVER['HTTP_USER_AGENT']`: The user's browser, which can be spoofed.
`$_SERVER['HTTP_REFERER']`: The previous page visited, which can be forged.
`$_SERVER['PHP_SELF']`: The current script's filename. An attacker can inject XSS by appending a malicious string to the URL, which is then reflected in a form's action attribute.
Best practice: Always sanitize $_SERVER values if you intend to display them on a page or use them in file paths.

`$_SESSION`
What it is: A superglobal that stores data for the duration of a user's session. The data itself is stored on the server, not the client.
How it is user-controlled: While a user cannot directly alter session variables, the values they contain can come from user-controlled input (e.g., a form field). Additionally, attackers can use "session hijacking" or "session fixation" to manipulate a victim's session by stealing or setting a session ID cookie.
Security risks: **If you assign a session variable directly from an unfiltered $_GET or $_POST value**, the session becomes susceptible to malicious input.

`$_ENV`
What it is: A superglobal array of variables passed to the script from the environment in which the PHP parser is running.
How it is user-controlled: In certain server configurations, attackers may be able to manipulate environment variables, such as the PATH or temporary file locations, to execute malicious code.
Security risks: While uncommon for web requests, relying on environment variables that can be modified by a less-privileged user on a shared system is a risk.
