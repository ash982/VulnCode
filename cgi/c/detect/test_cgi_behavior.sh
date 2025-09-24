#!/bin/bash

# Test if a compiled program behaves like a CGI program

test_cgi_behavior() {
    local program="$1"
    
    if [ ! -x "$program" ]; then
        echo "Error: $program is not executable"
        return 1
    fi
    
    echo "Testing CGI behavior for: $program"
    echo "=================================="
    
    # Test 1: Check if it produces HTTP headers
    echo "Test 1: HTTP Headers"
    output=$(timeout 5s "$program" 2>/dev/null | head -10)
    
    if echo "$output" | grep -i "content-type" > /dev/null; then
        echo "✓ Produces Content-Type header"
    else
        echo "✗ No Content-Type header found"
    fi
    
    # Test 2: Test with CGI environment variables
    echo "Test 2: CGI Environment Response"
    CGI_output=$(QUERY_STRING="test=value" REQUEST_METHOD="GET" timeout 5s "$program" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$CGI_output" ]; then
        echo "✓ Responds to CGI environment variables"
        
        # Check if output changes with different QUERY_STRING
        CGI_output2=$(QUERY_STRING="name=John&age=25" REQUEST_METHOD="GET" timeout 5s "$program" 2>/dev/null)
        if [ "$CGI_output" != "$CGI_output2" ]; then
            echo "✓ Output varies with different input"
        fi
    else
        echo "✗ No response to CGI environment"
    fi
    
    # Test 3: Check for HTML output
    echo "Test 3: HTML Output"
    if echo "$output" | grep -i -E "(<html|<body|<form)" > /dev/null; then
        echo "✓ Produces HTML output"
    else
        echo "? No obvious HTML output"
    fi
    
    echo ""
}

# Usage
if [ "$1" ]; then
    test_cgi_behavior "$1"
else
    echo "Usage: $0 <compiled_program>"
fi
