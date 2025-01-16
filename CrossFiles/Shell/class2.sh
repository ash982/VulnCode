#!/bin/bash

process_class2() {
    local input="$1"
    echo "Class2 processing: $input"
    # Potentially unsafe operation
    query="SELECT * FROM users WHERE username = '$input'"
    echo "Executing query: $query"
    # Simulating database query execution
    sqlite3 example.db "$query"
}
