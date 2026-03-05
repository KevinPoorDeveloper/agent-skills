---
name: "search-google-places"
description: "Search for places/businesses by category in specific locations using Google Places API with reviews and photos."
version: "1.0.0"
author: "Agent Zero"
tags:
  - google
  - places
  - api
  - search
  - restaurants
  - businesses
trigger_patterns:
  - "search places"
  - "find restaurants"
  - "google places"
  - "nearby places"
  - "find businesses"
  - "local search"
---

# Search Google Places API

Search for places/businesses by category in specific locations.

## When to Use

Use this skill when you need to:
- Find restaurants, cafes, or businesses in a location
- Get ratings, reviews, and photos for places
- Search by category (sushi_restaurant, coffee_shop, etc.)

## Important: Top 5 Results Only

This skill **always returns the top 5 places sorted by rating** (highest first).

## Usage

### Python Import
```python
import sys
sys.path.insert(0, '/a0/usr/skills/search-google-places/scripts')
from search_google_places_api import search_google_places_api

result = search_google_places_api(
    categories=["sushi_restaurant"],
    city="Seattle",
    state="WA",
    country="USA",
    max_results=5,
    include_reviews=True
)
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| categories | ✅ | - | Place types like ["sushi_restaurant"] |
| city | ✅ | - | City name |
| country | ✅ | - | Country name |
| neighborhood | ❌ | None | Specific area within city |
| state | ❌ | None | State/province |
| keyword | ❌ | None | Natural language search terms |
| max_results | ❌ | 5 | Initial results to fetch (1-20) |
| include_reviews | ❌ | False | Fetch user reviews + AI synthesis |
| include_photos | ❌ | False | Fetch photo URLs |

## Common Categories

### Restaurants
- `sushi_restaurant`, `ramen_restaurant`, `pizza_restaurant`
- `italian_restaurant`, `mexican_restaurant`, `thai_restaurant`
- `fine_dining_restaurant`, `fast_food_restaurant`

### Cafes & Drinks
- `coffee_shop`, `cafe`, `tea_house`, `bar`, `wine_bar`

### Services
- `gym`, `spa`, `hair_salon`, `bank`, `pharmacy`

## Requirements

- `GOOGLE_PLACES_API_KEY` environment variable
- `VENICE_API_KEY` for review synthesis
