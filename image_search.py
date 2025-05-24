import requests
import sys
from pathlib import Path
from serpapi import GoogleSearch
from utils import extract_country_code_from_secondary_result
from typing import List, Dict, Optional

NUULS_UPLOAD_ENDPOINT = "https://i.nuuls.com/upload"

def upload_image_get_url(image_path: str) -> str | None:
    if not Path(image_path).is_file():
        print(f"[Uploader] Помилка: Файл не знайдено: {image_path}")
        return None

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            print(f"[Uploader] Відправляємо POST-запит на {NUULS_UPLOAD_ENDPOINT}...")
            resp = requests.post(NUULS_UPLOAD_ENDPOINT, files=files, timeout=30)
            print(f"[Uploader] HTTP Status: {resp.status_code} {resp.reason}")

            if resp.status_code == 200:
                text = resp.text.strip()
                print(f"[Uploader] Текст відповіді від Nuuls: {text}")
                if text.startswith("http://") or text.startswith("https://"):
                    print(f"[Uploader] URL отримано (текстова відповідь): {text}")
                    return text
                try:
                    data = resp.json()
                    if isinstance(data, list) and data and "id" in data[0] and data[0]["id"]:
                        url = f"https://i.nuuls.com/{data[0]['id']}"
                        print(f"[Uploader] URL отримано (JSON відповідь): {url}")
                        return url
                    else:
                        print(f"[Uploader] Неочікуваний формат JSON: {data}")
                except requests.exceptions.JSONDecodeError:
                    print(f"[Uploader] Відповідь не є валідним JSON, хоча статус 200. Текст: {text}")
                except Exception as e_json:
                    print(f"[Uploader] Помилка обробки JSON відповіді: {e_json}")
            else:
                print(f"[Uploader] Помилка сервера Nuuls. Текст відповіді: {resp.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"[Uploader] Помилка завантаження на Nuuls (requests exception): {e}")
    except Exception as e:
        print(f"[Uploader] Загальна помилка під час завантаження: {e}")
    return None

def lens_search_image(image_url: str, serpapi_key: str, country: Optional[str] = None) -> Optional[dict]:
    if not image_url:
        print("[Lens] Не надано URL зображення для пошуку.")
        return None
    try:
        print(f"[Lens] Виконуємо пошук для URL: {image_url}")
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
        print("[Lens] Пошук успішний.")
        return data
    except requests.RequestException as e:
        print(f"[Lens] HTTP помилка: {e}")
    except ValueError as e:
        print(f"[Lens] Помилка JSON-декодування: {e}")
    return None
