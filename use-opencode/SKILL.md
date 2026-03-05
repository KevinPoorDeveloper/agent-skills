---
name: "use-opencode"
description: "Use OpenCode CLI to edit files, refactor code, and modify skills. Ideal for large file edits where rewriting entire files through code_execution_tool is error-prone. Runs OpenCode in single-turn non-interactive mode via 'opencode run'. Supports build mode (edits files) and plan mode (read-only analysis)."
version: "1.0.0"
author: "Model Creativity Inc"
tags: ["editing", "coding", "opencode", "files", "refactoring", "skills"]
trigger_patterns:
  - "edit file"
  - "edit skill"
  - "opencode"
  - "refactor"
  - "modify large file"
  - "surgical edit"
  - "update code"
  - "analyze code"
  - "code review"
  - "plan mode"
---

# Use OpenCode

OpenCode is a terminal-based AI coding assistant by SST. This skill uses it in **single-turn non-interactive mode** to make surgical file edits that would be error-prone or expensive if done by rewriting entire files.

## When to Use This Skill

- **Large file edits** — editing files with 100+ lines where rewriting is risky
- **Surgical changes** — changing specific functions, classes, or sections
- **Refactoring** — renaming, extracting functions, restructuring code
- **Skill editing** — modifying SKILL.md files or skill scripts
- **Multi-file changes** — OpenCode can navigate a project and edit multiple files
- **Any time you would otherwise rewrite an entire file through code_execution_tool**
- **Code analysis** — understanding what code does without changing it
- **Code review** — finding bugs, security issues, and improvements

## When NOT to Use This Skill

- Simple one-liner changes (just use `sed` or `code_execution_tool`)
- Creating brand new files from scratch (just write them directly)
- Non-code tasks (research, browsing, etc.)

## Prerequisites / Setup

Run the setup script if OpenCode is not yet installed:

```bash
bash /a0/usr/skills/use-opencode/scripts/setup.sh
```

This will:
1. Install OpenCode via the official install script
2. Create the global config at `~/.config/opencode/opencode.json`
3. Verify the installation

## Usage

### Basic Pattern

Always use `code_execution_tool` with `runtime: terminal` to invoke OpenCode:

```bash
export VENICE_API_KEY="<your-venice-api-key>"
cd /path/to/project/or/directory
opencode run "Your detailed instruction here"
```

### Standard Edit Command

Use the wrapper script for convenience:

```bash
bash /a0/usr/skills/use-opencode/scripts/edit.sh "<VENICE_API_KEY>" "/path/to/working/directory" "Your detailed edit instruction" [model] [mode]
```

The optional 5th parameter `mode` can be `"build"` (default, makes changes) or `"plan"` (read-only analysis). See [Plan Mode](#plan-mode-read-only-analysis) below.

### Direct Command (Alternative)

You can also call OpenCode directly:

```bash
export VENICE_API_KEY="<your-venice-api-key>"
cd /path/to/directory
opencode --model venice/claude-opus-4-6 run "In file src/auth.py, refactor the login() function to use async/await and add proper error handling"
```

### Specifying a Different Model

To use a model other than the default:

```bash
bash /a0/usr/skills/use-opencode/scripts/edit.sh "<VENICE_API_KEY>" "/path/to/dir" "instruction" "venice/llama-3.3-70b"
```

### Plan Mode (Read-Only Analysis)

Plan mode uses the `--agent plan` flag to restrict OpenCode to read-only tools (read, list, grep, glob, LSP). No files are modified in plan mode — it is purely for analysis and review.

**Via wrapper script:**

```bash
bash /a0/usr/skills/use-opencode/scripts/edit.sh "<VENICE_API_KEY>" "/path/to/dir" "Your analysis instruction" "venice/claude-opus-4-6" "plan"
```

**Via direct command:**

```bash
opencode --model venice/claude-opus-4-6 --agent plan run "Analyze the auth module for security issues"
```

**Example use cases:**

- Code analysis — understanding what code does and how it works
- Code review — finding bugs, security issues, and improvements
- Architecture review — evaluating project structure and patterns
- Planning refactors — scoping changes before implementing them
- Understanding unfamiliar code — exploring a new codebase without risk

## Writing Effective Prompts

The quality of edits depends heavily on the prompt. Follow these guidelines:

### Be Specific About Files
```
Good: "In file src/utils/parser.py, add input validation to the parse_json() function"
Bad:  "Add validation to the parser"
```

### Describe the Change Clearly
```
Good: "In SKILL.md, add a new ## Troubleshooting section after ## Usage with three common issues and solutions"
Bad:  "Update the skill docs"
```

### Include Context When Needed
```
Good: "In scripts/deploy.sh, the S3_BUCKET variable on line ~15 is hardcoded. Change it to read from the environment variable AWS_S3_BUCKET with a fallback to the current value"
Bad:  "Fix the deploy script"
```

### For Skill Editing Specifically
```
"In the SKILL.md file, update the version from 1.0.0 to 1.1.0 in the frontmatter, and add a new procedure under ## Usage called 'Batch Processing' that describes how to process multiple files"
```

## Best Practices & Lessons Learned

### Always Write Long Instructions to a Temp File

Bash will mangle instructions containing special characters like `!` (history expansion), `$` (variable expansion), backticks, and nested quotes. This causes cryptic errors like `bash: !: event not found`.

**Always use this pattern for non-trivial instructions:**

```python
# In code_execution_tool with runtime: python
instruction = r' ' '  Your long instruction here... can contain any characters safely ' ' '
with open('/tmp/opencode_instruction.txt', 'w') as f:
    f.write(instruction)
```

Then in terminal:
```bash
export VENICE_API_KEY="your-key"
cd /path/to/project
INSTRUCTION=$(cat /tmp/opencode_instruction.txt)
opencode --model venice/claude-opus-4-6 run "$INSTRUCTION"
```

This is the **most reliable invocation pattern** and should be the default approach for any instruction longer than a single sentence.

### Wait for OpenCode Output in Agent Zero

OpenCode typically takes 15-60 seconds for complex edits. The Agent Zero framework may return control before OpenCode finishes. Always follow an OpenCode invocation with a `runtime: "output"` call to wait for completion:

```json
{
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "output",
        "session": 0
    }
}
```

This ensures you see the full edit output, LSP diagnostics, and confirmation before proceeding.

### Combine Multi-File Edits Into One Call

OpenCode can read and edit multiple files in a single invocation. Instead of making separate calls for each file, describe all changes in one comprehensive instruction:

**Inefficient (multiple calls):**
```
Call 1: "Update SKILL.md with new documentation"
Call 2: "Write the main Python script"
Call 3: "Create the config file"
```

**Efficient (single call):**
```
"Create/update the following files in this project:
1. SKILL.md - full documentation with frontmatter, description, usage...
2. scripts/main.py - complete Python script that does X, Y, Z...
3. config/settings.json - configuration with these defaults..."
```

This cuts LLM cost and time proportionally. OpenCode naturally reads the full project tree so it has context for all files.

### Reference Existing Files for Context

When your edit depends on understanding another file's API or structure, tell OpenCode to read it:

```
"Read the venice-image-gen skill at ../venice-image-gen/scripts/generate_image.py to understand its function signatures, then write a script that calls it correctly."
```

OpenCode will automatically read referenced files and use their structure to produce compatible code.

### Always Verify After Each Edit

Since OpenCode runs in single-turn mode (no corrections mid-stream), always verify results before moving on:

```bash
# Quick syntax check for Python
python3 -c "import py_compile; py_compile.compile('file.py', doraise=True)"

# Check key content
grep -n 'function_name\|class_name' file.py

# Run tests if available
python -m pytest tests/
```

If something is wrong, craft a focused correction instruction for the next OpenCode call.

## Managing Models

To refresh and list available models:

```bash
opencode models --refresh
```

To just list current models:

```bash
opencode models
```

## Available Venice Models (as of 2026-03)

| Model | Best For |
|---|---|
| `venice/claude-opus-4-6` | **Default** — complex edits, refactoring, best quality |
| `venice/claude-sonnet-4-6` | Fast edits, good quality, cheaper |
| `venice/deepseek-v3.2` | Code-focused tasks |
| `venice/llama-3.3-70b` | Quick simple edits, very fast |
| `venice/qwen3-coder-480b-a35b-instruct` | Large codebase understanding |

## Workflow Pattern

When using OpenCode for edits, follow this pattern:

0. **Decide the mode** — use `plan` for analysis/review, `build` for making changes
0.5. **Write instruction to temp file** if it contains special characters or is longer than one sentence (see Best Practices)
1. **Craft a clear, specific prompt** describing exactly what to change
2. **Run OpenCode** via the edit script or direct command
3. **Verify the result** — read the file afterward to confirm the edit was applied correctly
4. **If incorrect** — run a new OpenCode command with a more specific correction (single-turn, no session continuity)

## Troubleshooting

### OpenCode Not Found
Run the setup script: `bash /a0/usr/skills/use-opencode/scripts/setup.sh`

### API Key Issues
Ensure VENICE_API_KEY is exported before running OpenCode. The wrapper script handles this automatically.

### Model Not Available
Refresh the model list: `opencode models --refresh`

### Edit Not Applied
OpenCode may ask for confirmation in some cases. If output shows a prompt, the edit may not have been applied. Re-run with a more explicit instruction.

### Large Project Indexing
For large projects, OpenCode may take time to index. The first run in a directory may be slower.

### Bash Escaping Errors
If you see `bash: !: event not found` or similar escaping errors, you are passing the instruction directly in bash. Write it to a temp file first using Python's raw strings (see Best Practices section above).

### OpenCode Appears to Produce No Output
OpenCode may take 15-60 seconds for complex edits. Use `runtime: "output"` in Agent Zero's code_execution_tool to wait for the full output. Do not assume failure if there is no immediate output.
