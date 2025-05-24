import requests
from typing import Optional

def lens_search_image(image_url: str, serpapi_key: str, country: Optional[str] = None) -> Optional[dict]:
    if not image_url:
        print("[Lens] No URL to search.")
        return None
    try:
        print(f"[Lens] Searching image by URL: {image_url}")
        lens_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": serpapi_key,
            "country": country,
        }
        response = requests.get(lens_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        print("[Lens] Success.")
        return data
    except requests.RequestException as e:
        print(f"[Lens] HTTP error: {e}")
    except ValueError as e:
        print(f"[Lens] Error JSON-decoding: {e}")
    return None
