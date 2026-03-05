---
name: "browser-use-cloud"
description: "Run AI-powered browser automation tasks via Browser Use Cloud API. Automates web scraping, structured data extraction, form filling, authenticated workflows, and any browser task using natural language. Features stealth anti-detect browsers with automatic CAPTCHA solving, Cloudflare bypass, and residential proxies in 195+ countries."
version: "1.1.0"
author: "Agent Zero"
tags: ["browser", "automation", "scraping", "extraction", "web", "stealth", "captcha", "proxy"]
trigger_patterns:
  - "browser use"
  - "browser automation"
  - "web scraping"
  - "extract data from website"
  - "scrape website"
  - "automate browser"
  - "fill form"
  - "browser task"
  - "stealth browser"
  - "captcha"
---

# Browser Use Cloud

Automate any browser task with natural language using the Browser Use Cloud API.
Every browser session includes anti-detect fingerprinting, automatic CAPTCHA solving,
ad/cookie blocking, Cloudflare bypass, residential proxies, and automatic output file downloading — zero configuration needed.

## Prerequisites

- **SDK**: `pip install browser-use-sdk`
- **API Key**: Set environment variable `BROWSER_USE_API_KEY` (use Agent Zero secret placeholder in tool calls)
- **Script**: `/a0/usr/skills/browser-use-cloud/scripts/browser_use.py`

## Quick Reference

| Command | What It Does |
|---------|--------------|
| `run "task"` | Run a browser task, get text output |
| `extract "task" --schema \'{...}\'` | Run a task, get structured JSON data back |
| `session create` | Create a reusable browser session |
| `session stop <id>` | Stop a session (saves profile state) |
| `billing` | Check account balance and plan info |
| `profiles` | List saved browser profiles |
| `browsers` | List active browser sessions |

## Environment Setup

Before running any command, ensure the API key is exported:

```bash
export BROWSER_USE_API_KEY="your_api_key_here"
```

All commands below assume this variable is set.

---

## Command 1: `run` — Run a Browser Task

Send a natural language instruction to an AI-controlled stealth browser.
The agent navigates, clicks, types, and returns text results.

### Syntax

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "<TASK>" [OPTIONS]
```

### Options

| Flag | Description | Example |
|------|-------------|---------|
| `--model` / `-m` | LLM model to use | `-m browser-use-llm` |
| `--start-url` / `-u` | Navigate directly to this URL first (saves steps/cost) | `-u https://example.com` |
| `--proxy` / `-p` | Residential proxy country code | `-p gb` |
| `--session-id` / `-s` | Attach to an existing session | `-s abc-123` |
| `--allowed-domains` | Restrict agent to these domains only | `--allowed-domains github.com *.github.io` |
| `--secrets` | Domain-scoped login credentials | `--secrets "github.com=user:pass"` |
| `--system-prompt` | Append custom instructions to the agent | `--system-prompt "Always click Accept cookies first"` |
| `--max-steps` | Max agent steps (default: 100) | `--max-steps 20` |
| `--flash` | Flash mode — faster but less careful | `--flash` |
| `--thinking` | Extended reasoning mode | `--thinking` |
| `--judge` | Quality verification of output | `--judge` |
| `--stream` | Stream step-by-step progress as JSON lines | `--stream` |
| `--output-dir` / `-o` | Directory to save output files (default: /a0/tmp/downloads/browser-use) | `-o /root/screenshots` |

### Available Models

| Model | API String | Cost/Step | Speed | Notes |
|-------|-----------|-----------|-------|-------|
| Browser Use 2.0 | `browser-use-2.0` | $0.006 | ~3s | Default, best balance |
| Browser Use LLM | `browser-use-llm` | $0.002 | ~3s | Cheapest, good quality |
| O3 | `o3` | $0.03 | ~8s | Most capable reasoning |
| Gemini 3 Pro | `gemini-3-pro-preview` | $0.03 | ~8s | Google frontier |
| Gemini Flash | `gemini-flash-latest` | $0.0075 | — | Fast Google model |
| Gemini Flash Lite | `gemini-flash-lite-latest` | $0.005 | — | Cheapest Google |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | $0.05 | ~8s | Anthropic frontier |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $0.05 | ~8s | Latest Claude |

Every task also has a **$0.01 initialization cost** regardless of model.

### Proxy Country Codes (Common)

`us` (default), `gb`, `de`, `fr`, `jp`, `au`, `br`, `in`, `kr`, `ca`, `es`, `it`, `nl`, `se`, `sg`
— 195+ countries supported.

### Examples

**Simple task:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "What is the top post on Hacker News right now?"
```

**With starting URL and cheaper model:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "Get the title and author of the first article" \
  -u https://news.ycombinator.com \
  -m browser-use-llm
```

**With UK proxy:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "What is the price of iPhone 16 on apple.com?" \
  -p gb
```

**With domain restriction and credentials:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "Log in and check my recent orders" \
  -u https://example.com/login \
  --secrets "example.com=myuser:mypass123" \
  --allowed-domains example.com
```

**Streaming step-by-step progress:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "Find the latest SpaceX launch date" --stream
```

### Output Format (JSON)

```json
{
  "status": "finished",
  "task_id": "e93c8c0b-...",
  "task_status": "TaskStatus.finished",
  "steps": 3,
  "output": "The top post on Hacker News is..."
}
```

---

## Command 2: `extract` — Structured Data Extraction

Extract structured, validated data from any website. You define a JSON schema,
and the agent returns data matching that exact structure.

### Syntax

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py extract "<TASK>" --schema \'{...}\' [OPTIONS]
```

### Schema Format (Simplified JSON)

The schema uses a simplified format where values are type strings:

| Type | Description |
|------|-------------|
| `"str"` | String field |
| `"int"` | Integer field |
| `"float"` | Float/decimal field |
| `"bool"` | Boolean field |
| `"str?"` | Optional string (append `?` to any type) |
| `[{...}]` | List of objects (nested schema) |
| `{...}` | Nested object |

### Schema Examples

**List of items:**
```json
{"items": [{"title": "str", "url": "str", "score": "int"}]}
```

**Single object with optional fields:**
```json
{"name": "str", "price": "float", "in_stock": "bool", "description": "str?"}
```

**Nested objects:**
```json
{"company": "str", "details": {"founded": "int", "ceo": "str", "employees": "int"}}
```

### Options

Same as `run` except no `--stream`, `--thinking`, `--judge`, `--secrets`, or `--system-prompt`.
Supports: `--model`, `--start-url`, `--session-id`, `--proxy`, `--allowed-domains`, `--max-steps`, `--flash`, `--output-dir` / `-o`.

### Examples

**Extract top Hacker News posts:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py extract \
  "Get the top 5 posts from Hacker News" \
  --schema \'{"items": [{"title": "str", "url": "str", "points": "int"}]}\' \
  -u https://news.ycombinator.com
```

**Extract product info:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py extract \
  "Get the name, price, and rating of the first product" \
  --schema \'{"name": "str", "price": "float", "rating": "float", "reviews": "int"}\' \
  -u https://www.amazon.com/dp/B0SOME_ASIN
```

**Extract with proxy (German pricing):**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py extract \
  "Get the pricing plans" \
  --schema \'{"plans": [{"name": "str", "price": "str", "features": "str"}]}\' \
  -u https://example.com/pricing \
  -p de
```

### Output Format (JSON)

```json
{
  "status": "finished",
  "task_id": "abc-123-...",
  "task_status": "TaskStatus.finished",
  "steps": 2,
  "data": {
    "items": [
      {"title": "Show HN: My Project", "url": "https://...", "points": 342},
      {"title": "Another Post", "url": "https://...", "points": 215}
    ]
  }
}
```

The `data` field contains your structured output matching the schema.

---

## Command 3: `session` — Session Management

Sessions let you run multiple tasks in the same browser (preserving cookies,
login state, tabs). Also required for live debugging via `live_url`.

### Create a Session

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py session create [--proxy CODE] [--profile-id ID]
```

Returns `session_id` and `live_url` (real-time browser view for debugging).

**Example:**
```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py session create --proxy us
```

Output:
```json
{"session_id": "sess-abc-123", "live_url": "https://live.browser-use.com/..."}
```

### Use a Session with Tasks

Pass the `session_id` to `run` or `extract`:

```bash
# First task: log in
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "Log into GitHub" \
  -s sess-abc-123 \
  --secrets "github.com=user:pass"

# Second task: same session, already logged in
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py run "Star the browser-use/browser-use repo" \
  -s sess-abc-123
```

### Stop a Session

**Important:** Always stop sessions when done. This saves profile state (cookies, localStorage)
and stops billing. Sessions left running continue to incur charges.

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py session stop <SESSION_ID>
```

### Delete a Session

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py session delete <SESSION_ID>
```

### Share a Session

Create a public URL for real-time viewing:

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py session share <SESSION_ID>
```

---

## Command 4: `billing` — Account Information

Check your current balance, plan, and rate limits.

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py billing
```

Output:
```json
{
  "name": "Default Project",
  "total_credits_usd": 10.0,
  "monthly_credits_usd": 0.0,
  "additional_credits_usd": 10.0,
  "rate_limit": 25,
  "plan": "Pay As You Go"
}
```

---

## Command 5: `profiles` — List Browser Profiles

Profiles persist cookies and localStorage across sessions.

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py profiles
```

---

## Command 6: `browsers` — List Active Browsers

```bash
python /a0/usr/skills/browser-use-cloud/scripts/browser_use.py browsers
```

---

## Auto-Download Output Files

When a `run` or `extract` task produces output files (screenshots, PDFs, saved pages, etc.), they are **automatically downloaded** to a local directory.

### Default Behavior
- Output files are saved to `/a0/tmp/downloads/browser-use/<task-id-prefix>/`
- The task ID prefix is the first 8 characters of the task UUID
- Files retain their original names from the browser agent
- Download happens automatically after task completion — no extra flags needed

### Custom Output Directory
Use `--output-dir` / `-o` to specify a different download location:

```bash
python browser_use.py run "Take a screenshot of google.com" --output-dir /root/screenshots
```

```bash
python browser_use.py extract "Get data from site" --schema '{...}' -o /root/data
```

### Output Format
After the main task JSON output, a second JSON line shows downloaded files:

```json
{
  "downloaded_files": [
    {
      "file_id": "uuid-of-file",
      "file_name": "screenshot.pdf",
      "saved_to": "/a0/tmp/downloads/browser-use/1f8d4faa/screenshot.pdf"
    }
  ]
}
```

### Tips
- The browser agent typically saves screenshots as PDF for full-page captures
- You can request specific output formats in your task prompt (e.g., "save as PNG")
- If a file download fails, a warning is printed to stderr but the task still succeeds
- The download directory is created automatically if it doesn't exist

---

## Cost Estimation Guide

| Scenario | Model | Est. Steps | Est. Cost |
|----------|-------|-----------|----------|
| Simple page read | browser-use-llm | 1-2 | $0.01-0.01 |
| Simple page read | browser-use-2.0 | 1-2 | $0.01-0.02 |
| Multi-page navigation | browser-use-2.0 | 5-10 | $0.04-0.07 |
| Form fill + submit | browser-use-2.0 | 3-8 | $0.03-0.06 |
| Complex multi-step | o3 | 10-20 | $0.31-0.61 |
| Data extraction | browser-use-llm | 1-3 | $0.01-0.02 |

Formula: **$0.01** (init) + **steps × cost/step**

---

## Tips & Best Practices

1. **Always use `--start-url`** when you know the target page — saves navigation steps and cost
2. **Use `browser-use-llm`** for simple extraction tasks — 3× cheaper, same speed
3. **Use `browser-use-2.0`** (default) for complex multi-step tasks — better reliability
4. **Use `--flash`** for speed when precision isn't critical
5. **Use `--thinking`** for complex reasoning tasks
6. **Use `--judge`** when output accuracy is critical (adds verification step)
7. **Use sessions** for multi-step workflows requiring login state
8. **Always stop sessions** when done to save costs and persist state
9. **Restrict domains** with `--allowed-domains` when using credentials for security
10. **Use proxies** for geo-specific content (prices, availability, localized sites)

## Error Handling

All errors are returned as JSON:
```json
{"error": "description of what went wrong", "traceback": "..."}
```

Common issues:
- **"BROWSER_USE_API_KEY not set"** — Export the API key first
- **Rate limited (429)** — SDK auto-retries; reduce concurrent tasks if persistent
- **Task timeout** — Increase `--max-steps` or simplify the task
- **Blocked by site** — Try different proxy country, disable `--flash`, use a profile

## Stealth Features (Automatic — No Configuration)

Every browser session automatically includes:
- 🕵️ Anti-detect browser fingerprinting
- 🤖 Automatic CAPTCHA solving
- 🚫 Ad and cookie banner blocking
- ☁️ Cloudflare / anti-bot bypass
- 🌐 Residential proxy (US default, or specify with `--proxy`)
