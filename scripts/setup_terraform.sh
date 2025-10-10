#!/bin/bash

# This script downloads and installs Terraform for macOS, detecting the correct architecture.

set -e # Exit immediately if a command exits with a non-zero status.

TERRAFORM_VERSION="1.2.0" # Using the same version as the CI/CD for consistency.
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH_NAME=$(uname -m)

# 1. Check if running on macOS
if [ "$OS_NAME" != "darwin" ]; then
    echo "Error: This script is intended for macOS only."
    echo "Please download Terraform for your OS from https://www.terraform.io/downloads.html"
    exit 1
fi

# 2. Determine the correct architecture
if [ "$ARCH_NAME" == "x86_64" ]; then
    TF_ARCH="amd64"
elif [ "$ARCH_NAME" == "arm64" ]; then
    TF_ARCH="arm64"
else
    echo "Error: Unsupported architecture: $ARCH_NAME"
    exit 1
fi

TF_ZIP="terraform_${TERRAFORM_VERSION}_${OS_NAME}_${TF_ARCH}.zip"
DOWNLOAD_URL="https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/${TF_ZIP}"
INSTALL_DIR="/usr/local/bin"

echo "Terraform will be installed for your system:"
echo "  OS: $OS_NAME"
echo "  Architecture: $TF_ARCH"
echo "  Version: $TERRAFORM_VERSION"
echo ""

# 3. Download Terraform
echo "Downloading Terraform from $DOWNLOAD_URL..."
# Use a temporary file for the download
TEMP_FILE=$(mktemp)
curl -L -o "$TEMP_FILE" "$DOWNLOAD_URL"

# 4. Unzip the file
echo "Unzipping Terraform..."
unzip -o "$TEMP_FILE" -d . # -o overwrites existing files, -d specifies output directory

# 5. Move the binary to the installation directory
echo "Moving terraform binary to ${INSTALL_DIR}..."
# Check for write permissions and use sudo if necessary
if [ -w "$INSTALL_DIR" ]; then
    mv terraform "$INSTALL_DIR"
else
    echo "Write permission to ${INSTALL_DIR} is required. You may be prompted for your password."
    sudo mv terraform "$INSTALL_DIR"
fi

# 6. Clean up
echo "Cleaning up..."
rm "$TEMP_FILE"

# 7. Verify installation
echo "Verifying installation..."
terraform --version

echo ""
echo "✅ Terraform version ${TERRAFORM_VERSION} has been successfully installed to ${INSTALL_DIR}/terraform"
echo "You can now run 'terraform' commands from your terminal."
