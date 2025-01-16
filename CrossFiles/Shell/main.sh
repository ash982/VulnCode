#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input>"
    exit 1
fi

tainted_input="$1"

# Call Class1
source class1.sh
process_class1 "$tainted_input"

# Call Class2
source class2.sh
process_class2 "$tainted_input"
