a typical file structure for a web server with CGI support (use bash):

Basic Web Server Structure
/var/www/
├── html/                          # Document root for static files
│   ├── index.html                # Main website homepage
│   ├── form.html                 # Static HTML forms
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
├── cgi-bin/                      # CGI executable scripts directory
│   ├── hello.cgi                 # Our bash CGI script
│   ├── form-handler.cgi          # Form processing script
│   ├── contact.cgi
│   └── data-api.cgi
└── logs/                         # Log files (optional)
    ├── access.log
    └── error.log

Complete Example Structure
/var/www/
├── html/
│   ├── index.html
│   ├── contact.html
│   ├── about.html
│   ├── css/
│   │   ├── main.css
│   │   └── form.css
│   ├── js/
│   │   ├── main.js
│   │   └── validation.js
│   ├── images/
│   │   ├── header-bg.jpg
│   │   ├── logo.png
│   │   └── icons/
│   │       ├── email.svg
│   │       └── phone.svg
│   └── downloads/
│       └── brochure.pdf
├── cgi-bin/
│   ├── hello.cgi                 # Simple greeting script
│   ├── form-handler.cgi          # Form processing
│   ├── guestbook.cgi             # Guestbook functionality
│   ├── file-upload.cgi           # File upload handler
│   ├── search.cgi                # Search functionality
│   ├── admin/
│   │   ├── login.cgi
│   │   └── dashboard.cgi
│   └── api/
│       ├── users.cgi
│       └── products.cgi
├── data/                         # Data storage (outside web root for security)
│   ├── users.txt
│   ├── guestbook.txt
│   ├── uploads/
│   │   ├── documents/
│   │   └── images/
│   └── config/
│       └── database.conf
├── templates/                    # HTML templates (optional)
│   ├── header.html
│   ├── footer.html
│   └── navigation.html
└── logs/
    ├── access.log
    ├── error.log
    └── cgi.log
