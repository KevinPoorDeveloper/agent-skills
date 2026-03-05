# Deep Research

Automated deep web research tool that performs multiple targeted searches, extracts content from sources, and synthesizes comprehensive expert-level reports in Markdown.

## Features

- Generates 10 varied search queries to cover different angles of a topic
- Performs DuckDuckGo web searches (no API key required)
- Scrapes and extracts main content from up to 20 unique sources
- Synthesizes findings into a structured Markdown report with:
  - Executive summary
  - Key findings as bullet points
  - Detailed source analysis
  - Full source references with links
- Auto-installs missing dependencies

## Prerequisites

```bash
pip install ddgs requests beautifulsoup4
```

Dependencies are auto-installed on first run if missing.

## Usage

```bash
python scripts/research_topic.py "your topic here"
```

### Examples

```bash
# Basic topic
python scripts/research_topic.py "quantum computing"

# Multi-word topic
python scripts/research_topic.py "machine learning in healthcare"

# Complex research question
python scripts/research_topic.py "CRISPR gene editing applications and ethical considerations"
```

## Output

- **stdout** -- Prints a summary (first ~80 lines) of the research report
- **File** -- Saves the full Markdown report to `/a0/tmp/research_<topic>.md`

### Report Structure

```
# Deep Research Report: <topic>
## Executive Summary
## Key Information & Findings
## Detailed Source Analysis
## All Source References
```

## How It Works

1. **Query generation** -- Creates 10 search queries covering fundamentals, applications, challenges, latest developments, etc.
2. **Web search** -- Searches each query via DuckDuckGo, collecting unique URLs
3. **Content extraction** -- Fetches and parses HTML from top sources using BeautifulSoup, extracting main content while removing navigation/footer elements
4. **Synthesis** -- Filters relevant sentences, deduplicates using content hashing, and assembles a structured report

## Environment Variables

None required. Uses DuckDuckGo for search (no API key needed).
