#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Function to install Miniconda ---
install_miniconda() {
    echo "A working Python and Pip environment was not found. Installing Miniconda..."

    # Define Miniconda installation directory
    # Using a temporary directory for the script and a home directory for the install
    MINICONDA_INSTALL_DIR="$HOME/miniconda"
    MINICONDA_SCRIPT_PATH="/tmp/miniconda.sh"

    # Set the installer name based on the system architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        MINICONDA_INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
    elif [ "$ARCH" = "aarch64" ]; then
        MINICONDA_INSTALLER="Miniconda3-latest-Linux-aarch64.sh"
    else
        echo "Unsupported architecture: $ARCH"
        exit 1
    fi

    # Download the Miniconda installer
    echo "Downloading Miniconda..."
    wget "https://repo.anaconda.com/miniconda/${MINICONDA_INSTALLER}" -O "$MINICONDA_SCRIPT_PATH"

    # Install Miniconda in batch mode (non-interactive) without prompts
    echo "Installing Miniconda to $MINICONDA_INSTALL_DIR..."
    bash "$MINICONDA_SCRIPT_PATH" -b -p "$MINICONDA_INSTALL_DIR"

    # Add the Miniconda bin directory to the PATH for the current shell session
    # This is crucial for the subsequent commands in this script to work
    export PATH="$MINICONDA_INSTALL_DIR/bin:$PATH"

    # Clean up the installer
    rm "$MINICONDA_SCRIPT_PATH"

    echo "Miniconda with Python 3 and Pip has been installed successfully."
}

# --- Main Python and Pip Check ---

# Check if python3 is installed AND if pip is available for it.
# If this combined check fails, install Miniconda.
if ! (command -v python3 &> /dev/null && python3 -m pip --version &> /dev/null); then
    install_miniconda
else
    echo "Found existing Python 3 and Pip installation."
fi


# --- Application Setup ---

# Use python3 -m pip to be explicit
echo "Installing Flask..."
python3 -m pip install flask

echo "Starting the server..."
python3 server.py