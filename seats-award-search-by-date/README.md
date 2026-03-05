# Seats Award Search by Date

> **Paid Subscription Required:** This skill uses the [Seats.aero](https://seats.aero/) **Partner API**, which requires an active **Pro subscription** ($9.99/month as of writing). It will not work with a free account. See [seats.aero/pricing](https://seats.aero/) for current pricing.

Comprehensive day-by-day award flight availability search across all mileage programs using the Seats.aero Partner API. Generates a self-contained HTML dashboard with calendar heatmaps, sortable availability tables, program comparison cards, and auto-generated insights. Optionally generates a 4K infographic via Venice.ai.

## Features

- **Day-by-day search** across a date range for one origin and multiple destinations
- **All mileage programs** queried simultaneously (or filter to a specific program)
- **HTML Dashboard** with:
  - Destination summary cards (best rates, availability coverage)
  - Calendar heatmaps color-coded by availability and cost
  - Sortable/filterable detailed availability table (all cabin classes)
  - Program comparison cards
  - Auto-generated key insights
- **Combined JSON output** with all raw API records and metadata
- **4K infographic** generation via Venice.ai (optional)
- **Web deployment** to a local webserver directory (optional)
- Dark theme, fully self-contained (no external assets)

## Prerequisites

```bash
pip install requests
export SEATS_AERO_API_KEY="your_seats_aero_key"    # Required (Pro subscription)
export VENICE_API_KEY="your_venice_key"             # Optional (for infographic)
```

This skill also depends on a shared library at `_seats_aero_lib/api.py` (expected in the parent directory).

## Usage

### Basic: Search one destination for a month

```bash
python scripts/award_search_by_date.py \
  --origin SEA \
  --destinations HND \
  --start-date 2026-08-01 \
  --end-date 2026-08-31
```

### Multiple destinations with specific program

```bash
python scripts/award_search_by_date.py \
  --origin SEA \
  --destinations HND,NRT,KIX \
  --start-date 2026-08-01 \
  --end-date 2026-08-31 \
  --source emirates \
  --cabin first \
  --skip-infographic
```

### Custom output directory

```bash
python scripts/award_search_by_date.py \
  --origin LAX \
  --destinations NRT,HND \
  --start-date 2026-07-01 \
  --end-date 2026-07-31 \
  --cabin business \
  --output-dir ./my-search-results
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--origin` | Yes | -- | Origin IATA airport code (e.g., `SEA`, `LAX`, `JFK`) |
| `--destinations` | Yes | -- | Comma-separated destination IATA codes (e.g., `HND,NRT`) |
| `--start-date` | Yes | -- | Start date (`YYYY-MM-DD`) |
| `--end-date` | Yes | -- | End date (`YYYY-MM-DD`) |
| `--source` | No | all | Filter to a specific mileage program (e.g., `emirates`, `united`) |
| `--cabin` | No | `business` | Cabin to highlight in reports (display only, does NOT filter API) |
| `--output-dir` | No | `/a0/usr/workdir/award-search-results` | Output directory |
| `--deploy` | No | `True` | Copy results to webserver public directory |
| `--no-deploy` | No | `False` | Skip web deployment |
| `--skip-infographic` | No | `False` | Skip Venice.ai infographic generation |
| `--api-key` | No | env var | Override `SEATS_AERO_API_KEY` |
| `--venice-key` | No | env var | Override `VENICE_API_KEY` |

## Output Files

1. **JSON** -- `award-search-<origin>-<dests>-<date>.json` with all raw records and metadata
2. **HTML** -- `award-search-<origin>-<dests>-<date>.html` self-contained dashboard
3. **PNG** -- `award-search-<origin>-<dests>-<date>-infographic.png` (optional, 4K)

## API Rate Limits

- Seats.aero Pro: **1,000 API calls/day** (resets midnight UTC)
- Each day x destination = 1 API call
- Example: 31 days x 2 destinations = 62 API calls
- 0.5s delay between calls

## Important Notes

- The `--cabin` option controls **display emphasis only** -- all cabin data is always fetched from the API
- Some programs may not appear in cached results; Live Search is commercial-only
- The shared library `_seats_aero_lib/api.py` must be accessible in the parent directory

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEATS_AERO_API_KEY` | Yes | Seats.aero Partner API key (Pro subscription) |
| `VENICE_API_KEY` | No | Venice.ai key for infographic generation |
