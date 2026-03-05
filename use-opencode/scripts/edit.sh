#!/bin/bash
# OpenCode Edit Wrapper for Agent Zero
# Usage: bash edit.sh <VENICE_API_KEY> <WORKING_DIR> "instruction" [model] [mode]
#   mode: "build" (default) - makes changes | "plan" - analysis only, read-only

set -e

# Arguments
VENICE_API_KEY="$1"
WORKING_DIR="$2"
INSTRUCTION="$3"
MODEL="${4:-venice/claude-opus-4-6}"
MODE="${5:-build}"

# Validate arguments
if [ -z "$VENICE_API_KEY" ] || [ -z "$WORKING_DIR" ] || [ -z "$INSTRUCTION" ]; then
    echo "❌ Usage: bash edit.sh <VENICE_API_KEY> <WORKING_DIR> "instruction" [model] [mode]"
    echo ""
    echo "  VENICE_API_KEY  - Your Venice AI API key"
    echo "  WORKING_DIR     - Directory to work in (project root)"
    echo "  instruction     - Natural language edit/analysis instruction"
    echo "  model           - Optional model override (default: venice/claude-opus-4-6)"
    echo "  mode            - Optional: build (default) or plan (read-only analysis)"
    exit 1
fi

# Validate directory
if [ ! -d "$WORKING_DIR" ]; then
    echo "❌ Directory does not exist: $WORKING_DIR"
    exit 1
fi

# Validate mode
if [ "$MODE" != "build" ] && [ "$MODE" != "plan" ]; then
    echo "❌ Invalid mode: $MODE (must be "build" or "plan")"
    exit 1
fi

# Export API key for OpenCode
export VENICE_API_KEY

# Ensure opencode is in PATH
export PATH="$HOME/.local/bin:$HOME/.opencode/bin:/usr/local/bin:$PATH"

# Check OpenCode is installed
if ! command -v opencode &> /dev/null; then
    echo "❌ OpenCode not found. Run setup first:"
    echo "   bash /a0/usr/skills/use-opencode/scripts/setup.sh"
    exit 1
fi

# Build the agent flag
AGENT_FLAG=""
if [ "$MODE" = "plan" ]; then
    AGENT_FLAG="--agent plan"
fi

# Run OpenCode in non-interactive mode
if [ "$MODE" = "plan" ]; then
    echo "🔍 OpenCode Plan (read-only analysis)"
else
    echo "🔧 OpenCode Build (editing)"
fi
echo "   Model: $MODEL"
echo "   Dir:   $WORKING_DIR"
echo "   Task:  $INSTRUCTION"
echo "---"

cd "$WORKING_DIR"
opencode --model "$MODEL" $AGENT_FLAG run "$INSTRUCTION"

echo "---"
if [ "$MODE" = "plan" ]; then
    echo "✅ OpenCode analysis complete (no files modified)"
else
    echo "✅ OpenCode edit complete"
fi
