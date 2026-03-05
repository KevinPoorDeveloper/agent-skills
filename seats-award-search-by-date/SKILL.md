---
name: seats-award-search-by-date
version: 1.0.0
description: Comprehensive day-by-day award flight availability search across ALL mileage programs for one origin and multiple destinations over a date range. Generates HTML dashboard with calendar heatmaps, availability tables, program comparison cards, key insights, and optional 4K infographic via Venice.ai.
author: Agent Zero
tags: [seats.aero, award-flights, mileage, availability, search, calendar, heatmap, dashboard, infographic, travel]
---

# seats-award-search-by-date

Perform a **comprehensive day-by-day award flight availability search** across ALL mileage programs for one origin and MULTIPLE destinations over a date range using the Seats.aero Partner API.

Produces a beautiful **dark-themed HTML dashboard** with calendar heatmaps, sortable availability tables, program comparison cards, and auto-generated key insights. Optionally generates a **4K infographic** via Venice.ai image generation.

## When to Use

- You want to find the **best dates and programs** for award flights over a month or date range
- You need to compare **multiple destinations** side-by-side (e.g., HND vs NRT for Tokyo)
- You want a **visual calendar overview** showing which days have availability and at what cost
- You need to compare **all mileage programs** to find the cheapest redemption
- You want a shareable **HTML report** or **4K infographic** summarizing award availability

## Usage

### Basic: Search one destination for a month

```bash
python /a0/usr/skills/seats-award-search-by-date/scripts/award_search_by_date.py \
  --origin SEA \
  --destinations HND \
  --start-date 2026-08-01 \
  --end-date 2026-08-31
```

### Advanced: Multiple destinations, specific program, skip infographic

```bash
python /a0/usr/skills/seats-award-search-by-date/scripts/award_search_by_date.py \
  --origin SEA \
  --destinations HND,NRT,KIX \
  --start-date 2026-08-01 \
  --end-date 2026-08-31 \
  --source emirates \
  --cabin first \
  --skip-infographic
```

### Full options with custom output

```bash
python /a0/usr/skills/seats-award-search-by-date/scripts/award_search_by_date.py \
  --origin LAX \
  --destinations NRT,HND \
  --start-date 2026-07-01 \
  --end-date 2026-07-31 \
  --cabin business \
  --output-dir /tmp/my-search \
  --deploy
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--origin` | Yes | — | Origin IATA airport code (e.g., SEA, LAX, JFK) |
| `--destinations` | Yes | — | Comma-separated destination IATA codes (e.g., HND,NRT) |
| `--start-date` | Yes | — | Start date in YYYY-MM-DD format |
| `--end-date` | Yes | — | End date in YYYY-MM-DD format |
| `--source` | No | all programs | Filter to a specific mileage program (e.g., emirates, united) |
| `--cabin` | No | business | Cabin class to highlight in reports (economy/premium/business/first). Display only — NOT used as API filter |
| `--output-dir` | No | /a0/usr/workdir/award-search-results | Directory for output files |
| `--deploy` | No | True | Copy HTML and infographic to /a0/webui/public/ for web access |
| `--skip-infographic` | No | False | Skip Venice.ai 4K infographic generation |
| `--api-key` | No | env SEATS_AERO_API_KEY | Override Seats.aero API key |
| `--venice-key` | No | env VENICE_API_KEY | Override Venice.ai API key |

## Output

The script produces:

1. **Combined JSON** — All raw API records merged into a single JSON file with metadata
2. **HTML Dashboard** — Self-contained dark-themed HTML file with:
   - Summary cards per destination (best rates, availability coverage)
   - Calendar heatmaps color-coded by business class availability
   - Sortable detailed availability table with all cabins
   - Program comparison cards
   - Auto-generated key insights
3. **4K Infographic** (optional) — AI-generated travel infographic via Venice.ai
4. **Web deployment** — Files copied to `/a0/webui/public/` for browser access

## Requirements

- **SEATS_AERO_API_KEY** environment variable (or `--api-key` argument) — Seats.aero Pro subscription required
- **VENICE_API_KEY** environment variable (or `--venice-key` argument) — Required only for infographic generation
- Python packages: `requests` (standard in Agent Zero environment)
- Shared library: `/a0/usr/skills/_seats_aero_lib/api.py`

## API Rate Limits

- Seats.aero Pro tier: **1,000 API calls/day** (resets midnight UTC)
- Each day × destination = 1 API call
- Example: 31 days × 2 destinations = 62 API calls
- Script adds 0.5s delay between calls to be respectful
- Venice.ai: 1 call for infographic generation

## Important Notes

- The `--cabin` option controls **display emphasis only** — it does NOT filter API results. All cabin data is always fetched.
- The script queries without `cabinClass` or `onlyDirectFlights` filters to get the most comprehensive results across all programs.
- Some programs (e.g., Delta business) may not appear in cached results — Live Search is commercial-only.
- Programs discovered in results may include ones not in official docs (e.g., lufthansa/Miles & More).
