#!/bin/bash

# Clear existing todo_list.txt
> todo_list.txt

# Find all Python and JavaScript files in backend and frontend directories and search for TODO comments
find ./backend ./frontend -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" \) -exec grep -Hn "TODO:" {} \; | \
while IFS=':' read -r file line content; do
    # Extract the TODO comment
    todo=$(echo "$content" | sed 's/.*TODO:\s*\(.*\)/\1/')
    # Get just the filename without path
    filename=$(basename "$file")
    # Write to todo_list.txt in specified format
    echo "$filename - $line | TODO: $todo" >> todo_list.txt
done

echo "TODO list has been generated in todo_list.txt"
