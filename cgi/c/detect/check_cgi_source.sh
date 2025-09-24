#!/bin/bash

# Script to analyze C/C++ source for CGI patterns

check_cgi_patterns() {
    local file="$1"
    echo "Analyzing: $file"
    echo "=========================="
    
    # Check for Content-Type header output
    if grep -i "content-type" "$file" > /dev/null; then
        echo "✓ Found Content-Type header output"
    fi
    
    # Check for CGI environment variables
    echo "CGI Environment Variables found:"
    grep -n "getenv" "$file" | grep -E "(QUERY_STRING|REQUEST_METHOD|CONTENT_LENGTH|HTTP_|SERVER_|REMOTE_)" || echo "  None found"
    
    # Check for HTML output
    if grep -E "(cout.*<|printf.*<)" "$file" > /dev/null; then
        echo "✓ Found HTML output patterns"
    fi
    
    # Check for form processing
    if grep -E "(QUERY_STRING|POST|form)" "$file" > /dev/null; then
        echo "✓ Found form processing indicators"
    fi
    
    # Check for CGI-specific headers
    echo "HTTP Headers found:"
    grep -n -E "(Content-Type|Location:|Set-Cookie)" "$file" || echo "  None found"
    
    echo ""
}

# Usage
if [ "$1" ]; then
    check_cgi_patterns "$1"
else
    echo "Usage: $0 <source_file.cpp>"
fi
