import requests
import sys
from pathlib import Path

# Додайте цю константу:
NUULS_UPLOAD_ENDPOINT = "https://i.nuuls.com/upload"

def upload_image_get_url(image_path: str) -> str | None:
    """
    Завантажує файл на nuuls.com і повертає URL завантаженого зображення.
    """
    if not Path(image_path).is_file():
        print(f"[Error] Файл не знайдено: {image_path}")
        return None

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            print(f"[Debug] Відправляємо POST на {NUULS_UPLOAD_ENDPOINT} ...")
            resp = requests.post(NUULS_UPLOAD_ENDPOINT, files=files)
            print(f"[Debug] HTTP {resp.status_code} {resp.reason}")
            text = resp.text.strip()
            print(f"[Debug] Nuuls response text: {text}")

            # Якщо відповідь — URL, повертаємо його
            if text.startswith("http://") or text.startswith("https://"):
                print(f"[Info] Отримано URL: {text}")
                return text

            # Інакше намагаємося JSON (fallback)
            try:
                data = resp.json()
                if isinstance(data, list) and data and "id" in data[0]:
                    url = f"https://i.nuuls.com/{data[0]['id']}"
                    print(f"[Info] Отримано URL із JSON: {url}")
                    return url
            except ValueError:
                pass

            print("[Error] Unexpected response format from Nuuls.")
    except Exception as e:
        print(f"[Error] Помилка при завантаженні: {e}")
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Використання: {sys.argv[0]} <path_to_image>")
        sys.exit(1)

    image_path = sys.argv[1]
    upload_image_get_url(image_path)
