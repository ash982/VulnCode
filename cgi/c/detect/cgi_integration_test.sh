#!/bin/bash

# Test CGI program integration

CGI_DIR="/var/www/cgi-bin"
TEST_URL="http://localhost/cgi-bin"

test_cgi_integration() {
    local program="$1"
    local program_name=$(basename "$program")
    
    echo "CGI Integration Test for: $program_name"
    echo "======================================"
    
    # Check if program is in CGI directory
    if [ -f "$CGI_DIR/$program_name" ]; then
        echo "✓ Found in CGI directory: $CGI_DIR"
        
        # Check permissions
        if [ -x "$CGI_DIR/$program_name" ]; then
            echo "✓ Executable permissions set"
        else
            echo "✗ Missing executable permissions"
        fi
        
        # Check ownership
        owner=$(ls -l "$CGI_DIR/$program_name" | awk '{print $3}')
        echo "Owner: $owner"
        
        # Test HTTP access (if curl is available)
        if command -v curl > /dev/null; then
            echo "Testing HTTP access..."
            response=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_URL/$program_name" 2>/dev/null)
            
            case $response in
                200) echo "✓ HTTP 200 - Program accessible and working" ;;
                500) echo "✗ HTTP 500 - Internal Server Error" ;;
                404) echo "✗ HTTP 404 - Not Found" ;;
                403) echo "✗ HTTP 403 - Forbidden" ;;
                *) echo "? HTTP $response - Unexpected response" ;;
            esac
        fi
        
    else
        echo "✗ Not found in CGI directory"
    fi
}

# Usage
if [ "$1" ]; then
    test_cgi_integration "$1"
else
    echo "Usage: $0 <program_name>"
fi
