from pathlib import Path
import requests
import re

NUULS_UPLOAD_ENDPOINT = "https://i.nuuls.com/upload"

def upload_image_get_url(image_path: str) -> str | None:
    if not Path(image_path).is_file():
        print(f"[Uploader] Error: File not found: {image_path}")
        return None

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            print(f"[Uploader] Sending POST-request on {NUULS_UPLOAD_ENDPOINT}...")
            resp = requests.post(NUULS_UPLOAD_ENDPOINT, files=files, timeout=30)
            print(f"[Uploader] HTTP Status: {resp.status_code} {resp.reason}")

            if resp.status_code == 200:
                text = resp.text.strip()
                print(f"[Uploader] Answer from Nuuls: {text}")
                if text.startswith("http://") or text.startswith("https://"):
                    print(f"[Uploader] URL received (text answer): {text}")
                    return text
                try:
                    data = resp.json()
                    if isinstance(data, list) and data and "id" in data[0] and data[0]["id"]:
                        url = f"https://i.nuuls.com/{data[0]['id']}"
                        print(f"[Uploader] URL received (JSON answer): {url}")
                        return url
                    else:
                        print(f"[Uploader] Unexpected JSON format: {data}")
                except requests.exceptions.JSONDecodeError:
                    print(f"[Uploader] Answer is not valid JSON, but status code = 200. Desc: {text}")
                except Exception as e_json:
                    print(f"[Uploader] Error processing JSON: {e_json}")
            else:
                print(f"[Uploader] Server error. Response: {resp.text[:500]}")
    except requests.exceptions.RequestException as e:
        print(f"[Uploader] Error uploading file (requests exception): {e}")
    except Exception as e:
        print(f"[Uploader] Error: {e}")
    return None

def extract_json_block(text: str) -> str:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_country_code(secondary_result: dict) -> str | None:
    if not secondary_result:
        return None
    hypotheses = secondary_result.get("new_location_hypotheses", [])
    for h in hypotheses:
        code = h.get("predicted_country_code")
        if code:
            return code.lower()
    return None