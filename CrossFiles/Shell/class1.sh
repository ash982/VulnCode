#!/bin/bash

process_class1() {
    local input="$1"
    echo "Class1 processing: $input"
    # Potentially unsafe operation
    eval "echo $input"
}
