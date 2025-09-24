# CGI keywords:

import cgi
import cgitb

# Create a FieldStorage object to parse GET/POST data
form = cgi.FieldStorage()
form.getvalue("username")


# You can also access the raw query string using os.environ
query_string = os.environ.get("QUERY_STRING", "")
print(f"<p>Raw Query String: {query_string}</p>")

This variable contains everything after the ? in the URL. os.environ.get() is used to safely retrieve the variable, providing an empty string as a default if it's not set.
example: http://your-domain.com/cgi-bin/your_script.py?name=Alice
