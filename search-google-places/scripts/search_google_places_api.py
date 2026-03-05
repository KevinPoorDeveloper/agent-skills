import requests
import json
import sys
import os

# Add venice_chat instrument to path
sys.path.insert(0, '/a0/instruments/custom/venice_chat')
from chat import chat as venice_chat


def synthesize_reviews(place_name: str, reviews: list) -> str:
    """
    Use Venice AI to synthesize reviews into 1-2 positive sentences.

    Args:
        place_name: Name of the place
        reviews: List of review dicts with 'text' field

    Returns:
        Synthesis string or empty string if failed
    """
    if not reviews:
        return ""

    # Combine review texts
    reviews_text = " | ".join([r.get("text", "")[:500] for r in reviews if r.get("text")])
    if not reviews_text:
        return ""

    try:
        result = venice_chat(
            message=f"Synthesize these reviews for {place_name} in 1 short sentence (max 100 characters). Focus on the highlight and vibe. Be concise. Reviews: {reviews_text}",
            system="You are a concise restaurant reviewer. Provide direct synthesis only - do not list review counts or mention how many reviews you analyzed.",
            model="grok-41-fast",
            temperature=0.7,
            max_tokens=50
        )
        return result.get("response", "").strip()
    except Exception as e:
        return ""


def search_google_places_api(
    categories: list,
    city: str,
    country: str,
    neighborhood: str = None,
    state: str = None,
    keyword: str = None,
    max_results: int = 5,
    include_reviews: bool = False,
    max_reviews: int = 3,
    include_photos: bool = False,
    max_photos: int = 3
) -> dict:
    """
    Search Google Places API for places by category in a specific location.

    Args:
        categories: List of place types (e.g., ["restaurant", "bank"])
        city: City name
        country: Country name
        neighborhood: Optional neighborhood/area within the city
        state: Optional state/province
        keyword: Optional search terms (e.g., "best sushi with great miso soup")
        max_results: Max results per category (1-20, default 5)
        include_reviews: Whether to fetch reviews for each place (extra API calls)
        max_reviews: Max reviews per place (1-5, default 3)
        include_photos: Whether to fetch photo URLs for each place (extra API calls)
        max_photos: Max photos per place (1-10, default 3)

    Returns:
        Dictionary with categories as keys and lists of places as values
    """

    API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if not API_KEY:
        return {"error": "GOOGLE_PLACES_API_KEY environment variable not set"}
    TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

    # Clamp values
    max_results = max(1, min(20, max_results))
    max_reviews = max(1, min(5, max_reviews))
    max_photos = max(1, min(10, max_photos))

    # Build location string (optimal order: neighborhood, city, state, country)
    location_parts = []
    if neighborhood:
        location_parts.append(neighborhood)
    location_parts.append(city)
    if state:
        location_parts.append(state)
    location_parts.append(country)
    location_string = ", ".join(location_parts)

    def get_place_details(place_id: str, get_reviews: bool, get_photos: bool) -> dict:
        """Fetch reviews and/or photos for a specific place using Place Details API."""
        fields = []
        if get_reviews:
            fields.append("reviews")
        if get_photos:
            fields.append("photos")

        if not fields:
            return {"reviews": [], "photos": []}

        params = {
            "place_id": place_id,
            "fields": ",".join(fields),
            "key": API_KEY
        }

        result = {"reviews": [], "photos": []}

        try:
            resp = requests.get(DETAILS_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") == "OK":
                place_result = data.get("result", {})

                # Process reviews
                if get_reviews:
                    reviews = place_result.get("reviews", [])
                    result["reviews"] = [{
                        "author": r.get("author_name"),
                        "rating": r.get("rating"),
                        "text": r.get("text"),
                        "time_description": r.get("relative_time_description"),
                        "language": r.get("language")
                    } for r in reviews[:max_reviews]]

                # Process photos
                if get_photos:
                    photos = place_result.get("photos", [])
                    result["photos"] = []
                    for photo in photos[:max_photos]:
                        photo_ref = photo.get("photo_reference")
                        if photo_ref:
                            photo_url = f"{PHOTO_URL}?maxwidth=800&photo_reference={photo_ref}&key={API_KEY}"
                            result["photos"].append({
                                "url": photo_url,
                                "width": photo.get("width"),
                                "height": photo.get("height"),
                                "attributions": photo.get("html_attributions", [])
                            })
        except Exception as e:
            pass

        return result

    results = {}

    for category in categories:
        # Build search query with optional keyword
        if keyword:
            query = f"{keyword} {category} in {location_string}"
        else:
            query = f"{category} in {location_string}"

        params = {
            "query": query,
            "type": category,
            "key": API_KEY
        }

        try:
            response = requests.get(TEXT_SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                results[category] = {
                    "error": data.get("status"),
                    "message": data.get("error_message", "Unknown error")
                }
                continue

            places = []
            for place in data.get("results", [])[:max_results]:
                place_id = place.get("place_id")

                place_info = {
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "price_level": place.get("price_level"),
                    "types": place.get("types", []),
                    "location": place.get("geometry", {}).get("location"),
                    "open_now": place.get("opening_hours", {}).get("open_now"),
                    "place_id": place_id,
                    "business_status": place.get("business_status")
                }

                # Fetch reviews and/or photos if requested
                if (include_reviews or include_photos) and place_id:
                    details = get_place_details(place_id, include_reviews, include_photos)
                    if include_reviews:
                        place_info["reviews"] = details["reviews"]
                    # Generate AI synthesis of reviews
                    place_info["review_synthesis"] = synthesize_reviews(
                        place_info["name"],
                        details["reviews"]
                    )
                    if include_photos:
                        place_info["photos"] = details["photos"]

                places.append(place_info)

            results[category] = {
                "count": len(places),
                "query_used": query,
                "location_searched": location_string,
                "places": places
            }

        except requests.exceptions.RequestException as e:
            results[category] = {
                "error": "request_failed",
                "message": str(e)
            }

    return results


# Example usage / test
if __name__ == "__main__":
    result = search_google_places_api(
        categories=["restaurant"],
        city="Seattle",
        neighborhood="Ballard",
        state="WA",
        country="USA",
        keyword="best sushi",
        max_results=2,
        include_reviews=True,
        max_reviews=2,
        include_photos=False
    )
    print(json.dumps(result, indent=2))
