#!/bin/bash
# OpenCode Setup Script for Agent Zero
# Installs OpenCode CLI and configures Venice AI provider

set -e

echo "========================================"
echo "  OpenCode Setup for Agent Zero"
echo "========================================"
echo ""

# Step 1: Install OpenCode
echo "[1/3] Installing OpenCode CLI..."
if command -v opencode &> /dev/null; then
    echo "  ✅ OpenCode already installed: $(opencode --version 2>/dev/null || echo 'version unknown')"
else
    echo "  📦 Downloading and installing..."
    curl -fsSL https://opencode.ai/install | bash
    # Ensure it's in PATH
    export PATH="$HOME/.local/bin:$HOME/.opencode/bin:/usr/local/bin:$PATH"
    if command -v opencode &> /dev/null; then
        echo "  ✅ OpenCode installed successfully"
    else
        echo "  ❌ Installation failed. Trying npm fallback..."
        npm install -g opencode-ai
        if command -v opencode &> /dev/null; then
            echo "  ✅ OpenCode installed via npm"
        else
            echo "  ❌ All installation methods failed. Please install manually."
            exit 1
        fi
    fi
fi

# Step 2: Create global config directory
echo ""
echo "[2/3] Creating global configuration..."
mkdir -p ~/.config/opencode

# Copy template config
cp /a0/usr/skills/use-opencode/config/opencode.json ~/.config/opencode/opencode.json
echo "  ✅ Config written to ~/.config/opencode/opencode.json"

# Step 3: Verify installation
echo ""
echo "[3/3] Verifying installation..."
echo "  OpenCode location: $(which opencode 2>/dev/null || echo 'not in PATH')"

# Try refreshing models if API key is available
if [ -n "$VENICE_API_KEY" ]; then
    echo "  🔄 Refreshing model list..."
    opencode models --refresh 2>/dev/null && echo "  ✅ Models refreshed" || echo "  ⚠️  Could not refresh models (may need auth setup)"
else
    echo "  ⚠️  VENICE_API_KEY not set - skipping model refresh"
    echo "     Set it and run: opencode models --refresh"
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Usage:"
echo "  bash /a0/usr/skills/use-opencode/scripts/edit.sh <VENICE_API_KEY> <WORKING_DIR> "instruction""
echo ""
