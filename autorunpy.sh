#!/bin/bash

# Directory containing Python scripts
SCRIPT_DIR="/config/a"

# Function to run a script in the background
run_script() {
  local script=$1
  while true; do
    echo "Starting $script..."
    python3 "$script"
    echo "$script stopped. Restarting in 5 seconds..."
    sleep 5
  done
}

# Export the function to allow running in subshells
export -f run_script

# Change to the script directory
cd "$SCRIPT_DIR" || { echo "Directory $SCRIPT_DIR not found!"; exit 1; }

# Find all Python scripts in the directory and run them in parallel
find . -type f -name "*.py" | while read -r script; do
  bash -c "run_script \"$script\"" &
done

# Wait for all background processes
wait