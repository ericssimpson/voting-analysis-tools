#!/bin/bash

# Directory containing the files
directory="dataverse_filese"

# Change to the directory
cd "$directory" || exit

# Iterate over each file in the directory
for file in *; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
        # Run your Python script with the file name as an argument
        python MDS_integration.py "$file"
    fi
done
