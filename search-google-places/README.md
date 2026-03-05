# Search Google Places

Search for businesses and places by category in specific locations using the Google Places API. Returns top results sorted by rating with optional review fetching and AI-powered review synthesis via Venice AI.

## Features

- Search by place category (restaurants, cafes, services, etc.) and location
- Filter by city, neighborhood, state, country
- Optional keyword filtering (e.g., "best sushi with great miso soup")
- Fetch user reviews with AI-generated review synthesis
- Fetch place photos with URLs
- Returns up to 20 results per category, sorted by rating

## Prerequisites

```bash
pip install requests
export GOOGLE_PLACES_API_KEY="your_google_api_key"
export VENICE_API_KEY="your_venice_key"  # Optional, for AI review synthesis
```

## Usage

This skill is used as a Python import:

```python
import sys
sys.path.insert(0, 'search-google-places/scripts')
from search_google_places_api import search_google_places_api

result = search_google_places_api(
    categories=["restaurant"],
    city="Seattle",
    neighborhood="Ballard",
    state="WA",
    country="USA",
    keyword="best sushi",
    max_results=5,
    include_reviews=True,
    max_reviews=2
)
```

Or run directly:

```bash
python scripts/search_google_places_api.py
```

(The `__main__` block runs a demo search for sushi restaurants in Ballard, Seattle.)

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `categories` | Yes | -- | List of place types (e.g., `["restaurant", "cafe"]`) |
| `city` | Yes | -- | City name |
| `country` | Yes | -- | Country name |
| `neighborhood` | No | `None` | Specific area within city |
| `state` | No | `None` | State/province |
| `keyword` | No | `None` | Natural language search terms |
| `max_results` | No | `5` | Results per category (1-20) |
| `include_reviews` | No | `False` | Fetch user reviews + AI synthesis |
| `max_reviews` | No | `3` | Reviews per place (1-5) |
| `include_photos` | No | `False` | Fetch photo URLs |
| `max_photos` | No | `3` | Photos per place (1-10) |

## Common Categories

**Restaurants:** `restaurant`, `sushi_restaurant`, `ramen_restaurant`, `pizza_restaurant`, `italian_restaurant`, `mexican_restaurant`, `thai_restaurant`, `fine_dining_restaurant`, `fast_food_restaurant`

**Cafes & Drinks:** `coffee_shop`, `cafe`, `tea_house`, `bar`, `wine_bar`

**Services:** `gym`, `spa`, `hair_salon`, `bank`, `pharmacy`

## Response Format

```json
{
  "restaurant": {
    "count": 5,
    "query_used": "best sushi restaurant in Ballard, Seattle, WA, USA",
    "location_searched": "Ballard, Seattle, WA, USA",
    "places": [
      {
        "name": "Example Sushi",
        "address": "123 Main St, Seattle, WA",
        "rating": 4.8,
        "user_ratings_total": 342,
        "price_level": 2,
        "types": ["restaurant", "food"],
        "location": {"lat": 47.67, "lng": -122.38},
        "open_now": true,
        "place_id": "ChIJ...",
        "business_status": "OPERATIONAL",
        "reviews": [...],
        "review_synthesis": "Outstanding fresh sushi with a cozy neighborhood vibe."
      }
    ]
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_PLACES_API_KEY` | Yes | Google Places API key |
| `VENICE_API_KEY` | No | Venice AI key for review synthesis |
