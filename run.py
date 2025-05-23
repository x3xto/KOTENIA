import os
import json
from visual_extractor import VisualOSINTAnalyzer
from secondary_analysis import conduct_secondary_analysis_with_gemini
from config import serapi_key
from image_search import upload_image_get_url, lens_search_image

IMAGE_PATH = r"D:\\photo_2025-04-10_02-34-04.jpg"
OUTPUT_PATH = os.path.join("output", "result.json")

if __name__ == "__main__":
    analyzer = VisualOSINTAnalyzer()
    result = analyzer.analyze_image(IMAGE_PATH)

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("[OK] Analysis complete. Result saved to:", OUTPUT_PATH)
    print("\n[Parsed Output]\n", json.dumps(result, indent=2, ensure_ascii=False))

    secondary_output_path = os.path.join("output", f"secondary_result.json")

    secondary_result = None
    secondary_result = conduct_secondary_analysis_with_gemini(IMAGE_PATH, result)
    if secondary_result:
        with open(secondary_output_path, "w", encoding="utf-8") as f:
            json.dump(secondary_result, f, indent=2, ensure_ascii=False)
        print("[Етап 2] Secondary analysis saved to:", secondary_output_path)
        print("\n[Secondary Analysis Output]\n", json.dumps(secondary_result, indent=2, ensure_ascii=False))
    else:
        print("[Етап 2] Аналіз не виконано.")

    # Етап 3.1: Google Lens через SerpAPI
    print("\n[Етап 3.1] Завантаження зображення і Lens-пошук...")
    image_url = upload_image_get_url(IMAGE_PATH)
    if image_url:
        lens_results = lens_search_image(image_url, serapi_key)
        lens_output_path = os.path.join("output", "lens_results.json")
        with open(lens_output_path, "w", encoding="utf-8") as f:
            json.dump(lens_results, f, indent=2, ensure_ascii=False)
        print("[Етап 3.1] Lens results saved to:", lens_output_path)
    else:
        print("[Етап 3.1] Lens search skipped — не вдалося отримати URL зображення.")
