# Browser Use Cloud

AI-powered browser automation via the [Browser Use Cloud API](https://browser-use.com/). Automate any browser task with natural language -- web scraping, structured data extraction, form filling, and authenticated workflows.

Every session includes stealth anti-detect fingerprinting, automatic CAPTCHA solving, ad/cookie blocking, Cloudflare bypass, and residential proxies in 195+ countries.

## Features

- **Natural language tasks** -- describe what you want in plain English
- **Structured data extraction** -- define a JSON schema and get validated data back
- **Session management** -- persist login state, cookies, and tabs across tasks
- **Stealth browsing** -- anti-detect fingerprinting, CAPTCHA solving, Cloudflare bypass
- **Proxy support** -- residential proxies in 195+ countries
- **Multiple LLM models** -- choose speed vs. capability vs. cost
- **Auto file download** -- output files (screenshots, PDFs) saved automatically

## Prerequisites

```bash
pip install browser-use-sdk
export BROWSER_USE_API_KEY="your_api_key_here"
```

## Usage

### Run a browser task

```bash
python scripts/browser_use.py run "What is the top post on Hacker News right now?"
```

### With a starting URL (saves steps and cost)

```bash
python scripts/browser_use.py run "Get the title of the first article" \
  -u https://news.ycombinator.com \
  -m browser-use-llm
```

### Extract structured data

```bash
python scripts/browser_use.py extract \
  "Get the top 5 posts from Hacker News" \
  --schema '{"items": [{"title": "str", "url": "str", "points": "int"}]}' \
  -u https://news.ycombinator.com
```

### Session workflow (preserving login state)

```bash
# Create a session
python scripts/browser_use.py session create --proxy us

# Run tasks in that session
python scripts/browser_use.py run "Log into GitHub" -s <session_id> --secrets "github.com=user:pass"
python scripts/browser_use.py run "Star the browser-use repo" -s <session_id>

# Stop when done (saves state, stops billing)
python scripts/browser_use.py session stop <session_id>
```

### Check billing

```bash
python scripts/browser_use.py billing
```

## Commands

| Command | Description |
|---------|-------------|
| `run "task"` | Run a browser task, get text output |
| `extract "task" --schema '{...}'` | Run a task, get structured JSON data |
| `session create` | Create a reusable browser session |
| `session stop <id>` | Stop a session (saves profile state) |
| `session delete <id>` | Delete a session |
| `session share <id>` | Create a shareable viewing link |
| `billing` | Check account balance and plan |
| `profiles` | List saved browser profiles |
| `browsers` | List active browser sessions |

## Run Options

| Flag | Description |
|------|-------------|
| `--model` / `-m` | LLM model to use |
| `--start-url` / `-u` | Navigate directly to this URL first |
| `--proxy` / `-p` | Residential proxy country code (e.g., `us`, `gb`, `de`) |
| `--session-id` / `-s` | Attach to an existing session |
| `--allowed-domains` | Restrict navigation to these domains |
| `--secrets` | Domain-scoped credentials (`domain=user:pass`) |
| `--system-prompt` | Custom instructions appended to the agent |
| `--max-steps` | Maximum agent steps (default: 100) |
| `--flash` | Flash mode -- faster but less careful |
| `--thinking` | Extended reasoning mode |
| `--judge` | Quality verification of output |
| `--stream` | Stream step-by-step progress as JSON lines |
| `--output-dir` / `-o` | Custom directory for downloaded output files |

## Available Models

| Model | Cost/Step | Speed | Notes |
|-------|-----------|-------|-------|
| `browser-use-2.0` | $0.006 | ~3s | Default, best balance |
| `browser-use-llm` | $0.002 | ~3s | Cheapest, good quality |
| `o3` | $0.03 | ~8s | Most capable reasoning |
| `gemini-flash-latest` | $0.0075 | -- | Fast Google model |
| `claude-sonnet-4-6` | $0.05 | ~8s | Latest Anthropic |

All tasks have a **$0.01 initialization cost** regardless of model.

## Output Format

```json
{
  "status": "finished",
  "task_id": "e93c8c0b-...",
  "task_status": "TaskStatus.finished",
  "steps": 3,
  "output": "The top post on Hacker News is..."
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BROWSER_USE_API_KEY` | Yes | Browser Use Cloud API key |
