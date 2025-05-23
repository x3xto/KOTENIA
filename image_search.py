import requests
from serpapi import GoogleSearch

NUULS_UPLOAD_ENDPOINT = "https://i.nuuls.com/upload"

def upload_image_get_url(image_path: str) -> str | None:
    """
    Завантажує файл на nuuls.com і повертає URL завантаженого зображення.
    """
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            resp = requests.post(NUULS_UPLOAD_ENDPOINT, files=files)
            resp.raise_for_status()
            data = resp.json()
            # Nuuls повертає список об'єктів з полем "id", з якого будуємо URL
            # Приклад структури: [{"id":"abcd1234"}]
            if isinstance(data, list) and data and "id" in data[0]:
                return f"https://i.nuuls.com/{data[0]['id']}"
    except Exception as e:
        print(f"[Lens] Помилка завантаження на Nuuls: {e}")
    return None

def lens_search_image(image_url: str, serpapi_key: str) -> dict:
    """
    Виконує Google Lens пошук через SerpAPI за URL зображення.
    Повертає сирий JSON-відповідь.
    """
    try:
        params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": serpapi_key,
            # опціонально: "hl": "en", "country": "us"
        }
        search = GoogleSearch(params)
        return search.get_dict()
    except Exception as e:
        print(f"[Lens] Помилка Google Lens search: {e}")
        return {}
