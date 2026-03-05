---
name: "deep-research"
description: "Conduct automated deep web research on any topic - performs multiple searches, reviews sources, and synthesizes comprehensive expert-level content."
version: "1.0.0"
author: "Agent Zero"
tags:
  - research
  - web
  - search
  - analysis
  - synthesis
trigger_patterns:
  - "deep research"
  - "research topic"
  - "comprehensive research"
  - "become expert"
  - "research about"
---

# Deep Research Tool

Conduct automated deep web research on any topic.

## When to Use

Use this skill when you need to:
- Quickly become an expert on a topic
- Conduct comprehensive multi-source research
- Generate expert-level summaries with citations

## Features

- Performs 5-10 targeted web searches
- Reviews 10-15+ unique sources
- Synthesizes ~1 page of expert-level content
- Includes source citations and references
- Saves full report to /a0/tmp/

## Usage

### Basic
```bash
python /a0/usr/skills/deep-research/scripts/research_topic.py "quantum computing"
```

### Multi-word Topics
```bash
python /a0/usr/skills/deep-research/scripts/research_topic.py "machine learning in healthcare"
```

### Complex Research
```bash
python /a0/usr/skills/deep-research/scripts/research_topic.py "CRISPR gene editing applications and ethical considerations"
```

## Output

- Prints expert-level content summary to stdout
- Saves full markdown report to `/a0/tmp/research_<topic>.md`
- Includes: Overview, Key Findings, Detailed Analysis, Source References

## Requirements

- `duckduckgo_search` (auto-installed if missing)
- `beautifulsoup4` (auto-installed if missing)
- `requests`
