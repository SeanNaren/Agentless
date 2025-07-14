#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Environment Activation ---
echo "Activating pre-existing Python 3.11 environment..."
# This command makes the python and pip from the environment available in the shell.
source /opt/miniconda3/bin/activate

# --- Sanity Check ---
# Verify which python is being used and its version.
echo "--------------------------------------------------"
echo "Using Python executable from activated environment:"
which python
python -V
echo "--------------------------------------------------"

# --- Application Setup ---
# Now we can use 'python' and 'pip' directly, as they point to the
# executables in the activated conda environment.

echo "Installing Flask..."
pip install --quiet flask

echo "Starting the server..."
python server.py
