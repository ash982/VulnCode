#!/bin/bash

analyze_binary() {
    local binary="$1"
    
    echo "Binary Analysis for: $binary"
    echo "=========================="
    
    # Check for CGI-related strings in binary
    echo "CGI-related strings found:"
    strings "$binary" | grep -i -E "(content-type|query_string|request_method|http_|cgi)" | head -10
    
    echo ""
    echo "Environment variable access:"
    strings "$binary" | grep -E "(getenv|environ)" | head -5
    
    echo ""
    echo "HTML-related strings:"
    strings "$binary" | grep -E "(<html|<body|<form|text/html)" | head -5
    
    echo ""
    echo "Networking/Web indicators:"
    nm "$binary" 2>/dev/null | grep -E "(getenv|printf|cout|cin)" || echo "Symbol table not available"
}

# Usage
if [ "$1" ]; then
    analyze_binary "$1"
else
    echo "Usage: $0 <binary_file>"
fi
