#!/bin/bash

# Step 1: Set up project directory
PROJECT_DIR="$1"
if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 <project-directory>"
    exit 1
fi

cd "$PROJECT_DIR" || { echo "Directory $PROJECT_DIR not found"; exit 1; }

# Step 2: Install all necessary packages in the local project environment
raco pkg install --auto

# Step 3: Run tests
echo "Running tests..."
raco test .

# Capture the exit code of the test command
TEST_RESULT=$?

# Step 4: Check the result and provide feedback
if [ $TEST_RESULT -eq 0 ]; then
    echo "All tests passed successfully."
    exit 0
else
    echo "Some tests failed."
    exit 1
fi
