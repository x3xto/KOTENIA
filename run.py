# run.py
import os
import json
from first_analysis import VisualOSINTAnalyzer
from secondary_analysis import conduct_secondary_analysis_with_gemini
from config import serapi_key
from image_search import upload_image_get_url, lens_search_image
from utils import extract_country_code_from_secondary_result

IMAGE_PATH = r"D:\\photo_2025-04-10_02-34-04.jpg"
OUTPUT_DIR = "output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "result.json")
SECONDARY_PATH = os.path.join(OUTPUT_DIR, "secondary_result.json")
LENS_PATH = os.path.join(OUTPUT_DIR, "lens_results.json")

if __name__ == "__main__":
    print("[RUN] Starting full analysis pipeline")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Етап 1: первинний аналіз
    analyzer = VisualOSINTAnalyzer()
    result = analyzer.analyze_image(IMAGE_PATH)

    if not isinstance(result, dict):
        print("[Error] Analysis failed:", result)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump({"error": result}, f, indent=2, ensure_ascii=False)
    else:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("[OK] Primary analysis saved to:", OUTPUT_PATH)
        print("\n[Parsed Output]\n", json.dumps(result, indent=2, ensure_ascii=False))

    # Етап 2: вторинний аналіз
    print("\n[Етап 2] Вторинний аналіз із зображенням та JSON.")
    secondary_result = conduct_secondary_analysis_with_gemini(IMAGE_PATH, result)
    if secondary_result:
        with open(SECONDARY_PATH, "w", encoding="utf-8") as f:
            json.dump(secondary_result, f, indent=2, ensure_ascii=False)
        print("[Етап 2] Secondary analysis saved to:", SECONDARY_PATH)
        print("\n[Secondary Analysis Output]\n", json.dumps(secondary_result, indent=2, ensure_ascii=False))
    else:
        print("[Етап 2] Secondary analysis failed.")
        exit(1)

    # Етап 3.1: Google Lens через SerpAPI
    print("\n[Етап 3.1] Завантаження зображення і Lens-пошук...")
    image_url = upload_image_get_url(IMAGE_PATH)
    if image_url:
        predicted_country = extract_country_code_from_secondary_result(secondary_result)
        lens_results = lens_search_image(image_url, serapi_key, country=predicted_country)
        if lens_results:
            with open(LENS_PATH, "w", encoding="utf-8") as f:
                json.dump(lens_results, f, indent=2, ensure_ascii=False)
            print("[Етап 3.1] Lens results saved to:", LENS_PATH)
        else:
            print("[Етап 3.1] Lens search failed.")
    else:
        print("[Етап 3.1] Lens search skipped — не вдалося отримати URL зображення.")
