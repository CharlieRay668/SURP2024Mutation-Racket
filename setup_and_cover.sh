#!/bin/bash

# Step 1: Set up project directory
PROJECT_DIR="$1"
if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory>"
    exit 1
fi

cd "$PROJECT_DIR" || { echo "Directory $PROJECT_DIR not found"; exit 1; }

# Step 2: Check if package already initialized
if [ ! -f "./info.rkt" ]; then
    echo "Initializing Racket package..."
    raco pkg new .
else
    echo "Package already initialized."
fi

# Step 3: Install all necessary packages in the local project environment
raco pkg install --auto

# Step 4: Compile the project
raco make .

# Step 5: Run tests with coverage
raco cover .

# Optional: If you want to see the generated HTML coverage report, you can open it
# xdg-open "coverage/index.html"  # For Linux
# open "coverage/index.html"  # For macOS

echo "Code coverage report generated."
