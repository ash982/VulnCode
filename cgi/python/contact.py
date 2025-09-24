#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import cgi
import cgitb
from database import save_contact_message
from config import EMAIL_SETTINGS

cgitb.enable()

def main():
    print("Content-Type: text/html\n")
    
    form = cgi.FieldStorage()
    
    if os.environ.get('REQUEST_METHOD') == 'POST':
        name = form.getvalue('name', '')
        email = form.getvalue('email', '')
        message = form.getvalue('message', '')
        
        # Save to database
        message_id = save_contact_message(name, email, message)
        
        print(f"""
        <html>
        <head><title>Message Sent</title></head>
        <body>
            <h1>Thank you, {cgi.escape(name)}!</h1>
            <p>Your message has been received. Reference ID: {message_id}</p>
            <a href="/">Return to Home</a>
        </body>
        </html>
        """)
    else:
        print("<html><body><h1>Method Not Allowed</h1></body></html>")

if __name__ == "__main__":
    main()
