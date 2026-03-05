# Use OpenCode

Integration skill for the [OpenCode CLI](https://opencode.ai/) -- a terminal-based AI coding assistant by SST. Runs OpenCode in single-turn non-interactive mode for surgical file edits, refactoring, code analysis, and code review.

## Features

- **Surgical file edits** -- edit specific functions/sections in large files without rewriting
- **Refactoring** -- rename, extract functions, restructure code
- **Multi-file changes** -- OpenCode navigates the project and edits multiple files in one call
- **Code analysis** (plan mode) -- read-only analysis, review, and architecture evaluation
- **Model selection** -- choose from multiple Venice AI models for speed vs. quality

## Prerequisites

1. Run the setup script:

```bash
bash scripts/setup.sh
```

This installs OpenCode and creates the global config at `~/.config/opencode/opencode.json`.

2. Set your API key:

```bash
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Using the wrapper script

```bash
bash scripts/edit.sh "<VENICE_API_KEY>" "/path/to/project" "Your edit instruction" [model] [mode]
```

- `model` -- optional, defaults to `venice/claude-opus-4-6`
- `mode` -- `build` (default, makes changes) or `plan` (read-only analysis)

### Build mode (edit files)

```bash
bash scripts/edit.sh "$VENICE_API_KEY" "./my-project" \
  "In src/auth.py, refactor the login() function to use async/await"
```

### Plan mode (read-only analysis)

```bash
bash scripts/edit.sh "$VENICE_API_KEY" "./my-project" \
  "Analyze the auth module for security issues" \
  "venice/claude-opus-4-6" "plan"
```

### Direct OpenCode commands

```bash
export VENICE_API_KEY="your_key"
cd /path/to/project
opencode --model venice/claude-opus-4-6 run "Your instruction here"
```

## Available Models

| Model | Best For |
|-------|----------|
| `venice/claude-opus-4-6` | Default -- complex edits, refactoring, best quality |
| `venice/claude-sonnet-4-6` | Fast edits, good quality, cheaper |
| `venice/deepseek-v3.2` | Code-focused tasks |
| `venice/llama-3.3-70b` | Quick simple edits, very fast |
| `venice/qwen3-coder-480b-a35b-instruct` | Large codebase understanding |

## Files

```
use-opencode/
  SKILL.md              # Agent-facing skill documentation
  README.md             # This file
  config/
    opencode.json       # OpenCode configuration (Venice AI provider)
  scripts/
    setup.sh            # Installation and setup script
    edit.sh             # Wrapper for running OpenCode edit/plan commands
```

## Writing Effective Prompts

Be specific about files and changes:

```
Good: "In file src/utils/parser.py, add input validation to the parse_json() function"
Bad:  "Add validation to the parser"
```

Include context when needed:

```
Good: "In scripts/deploy.sh, the S3_BUCKET variable on line ~15 is hardcoded.
       Change it to read from AWS_S3_BUCKET env var with a fallback."
Bad:  "Fix the deploy script"
```

## Best Practices

1. **Write long instructions to a temp file** -- Bash will mangle special characters (`!`, `$`, backticks). Write to a file first, then read it into the command.
2. **Combine multi-file edits** -- Describe all changes in one instruction to cut cost and time.
3. **Verify after each edit** -- OpenCode runs in single-turn mode. Read files afterward to confirm.
4. **Use plan mode first** -- For unfamiliar codebases, use plan mode to understand before editing.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice AI API key |
