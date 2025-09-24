#!/bin/bash

GUESTBOOK_FILE="/var/www/data/guestbook.txt"

echo "Content-Type: text/html"
echo ""

if [ "$REQUEST_METHOD" = "POST" ]; then
    # Read and process form data
    read -n $CONTENT_LENGTH POST_DATA
    
    # Parse name and message
    name=$(echo "$POST_DATA" | sed 's/.*name=\([^&]*\).*/\1/' | sed 's/%20/ /g')
    message=$(echo "$POST_DATA" | sed 's/.*message=\([^&]*\).*/\1/' | sed 's/%20/ /g')
    
    # Append to guestbook file
    echo "$(date): $name - $message" >> "$GUESTBOOK_FILE"
    
    echo "<h1>Thank you for signing our guestbook!</h1>"
    echo "<a href='/cgi-bin/guestbook.cgi'>View Guestbook</a>"
else
    # Display guestbook and form
    echo "<h1>Guestbook</h1>"
    echo "<h2>Recent Entries:</h2>"
    
    if [ -f "$GUESTBOOK_FILE" ]; then
        echo "<ul>"
        tail -10 "$GUESTBOOK_FILE" | while read line; do
            echo "<li>$line</li>"
        done
        echo "</ul>"
    fi
    
    echo "<h2>Sign Guestbook:</h2>"
    echo "<form method='post'>"
    echo "<input type='text' name='name' placeholder='Your Name' required><br>"
    echo "<textarea name='message' placeholder='Your Message' required></textarea><br>"
    echo "<button type='submit'>Sign Guestbook</button>"
    echo "</form>"
fi
