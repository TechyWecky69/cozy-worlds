#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${COZY_WORLDS_REPO:-https://github.com/TechyWecky69/cozy-worlds.git}"
INSTALL_DIR="${HOME}/.local/share/cozy-worlds"
BIN_DIR="${HOME}/.local/bin"

command -v git >/dev/null 2>&1 || { echo "Please install git first."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Please install Python 3 first."; exit 1; }

mkdir -p "$BIN_DIR" "$(dirname "$INSTALL_DIR")"

if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo "Updating Cozy Worlds..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    if [[ -e "$INSTALL_DIR" ]]; then
        echo "Found $INSTALL_DIR but it is not a Git repository. Move it out of the way first."
        exit 1
    fi
    echo "Installing Cozy Worlds..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/launcher.py"
ln -sfn "$INSTALL_DIR/launcher.py" "$BIN_DIR/cozy"

echo
echo "Cozy Worlds is installed!"
echo "Run it with: cozy"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo
    echo "$BIN_DIR is not currently in PATH."
    echo "Add this line to ~/.bashrc or ~/.zshrc:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo "Then open a new terminal."
fi
