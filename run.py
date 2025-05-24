import os
import json
from first_analysis import VisualOSINTAnalyzer
from secondary_analysis import conduct_secondary_analysis
from config import serapi_key
from image_search import lens_search_image
import utils
from image_cropper import crop_image_by_coordinates

IMAGE_PATH = r"D:\\photo_2025-04-10_02-34-04.jpg"
OUTPUT_DIR = "output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "first_result.json")
SECONDARY_PATH = os.path.join(OUTPUT_DIR, "secondary_result.json")
CROPPED_FRAGMENTS_DIR = os.path.join(OUTPUT_DIR, "cropped_fragments")
LENS_FRAGMENTS_RESULTS = {}

if __name__ == "__main__":
    print("[RUN] Starting full analysis pipeline")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    parsed_coordinates = utils.parse_bounding_box_coordinates(result)
    # print(parsed_coordinates)
    if parsed_coordinates:
        print(f"[RUN] Розпарсено {len(parsed_coordinates)} наборів координат для фрагментів.")
        local_fragment_paths = crop_image_by_coordinates(IMAGE_PATH, parsed_coordinates, CROPPED_FRAGMENTS_DIR)

        if local_fragment_paths:
            print(f"[RUN] Обрізано та збережено {len(local_fragment_paths)} фрагментів до: {CROPPED_FRAGMENTS_DIR}")
            
            for fragment_name, fragment_path in local_fragment_paths.items():
                print(f"\n[RUN] Обробка фрагмента: {fragment_name} ({fragment_path})")
                fragment_url = utils.upload_image_get_url(fragment_path)
                if fragment_url:
                    print(f"[RUN] Фрагмент '{fragment_name}' завантажено на: {fragment_url}")
                    print(f"[RUN] Запускаємо пошук Google Lens для фрагмента '{fragment_name}'...")

                    # predicted_country = utils.extract_country_code(secondary_result)
                    lens_results_fragment = lens_search_image(fragment_url, serapi_key, country="") 
                    
                    fragment_lens_filename = os.path.join(OUTPUT_DIR, f"lens_fragment_{fragment_name.replace(' ', '_')}.json")
                    if lens_results_fragment:
                        LENS_FRAGMENTS_RESULTS[fragment_name] = {"uploaded_url": fragment_url, "lens_data": lens_results_fragment}
                        with open(fragment_lens_filename, "w", encoding="utf-8") as f:
                            json.dump(lens_results_fragment, f, indent=2, ensure_ascii=False)
                        print(f"[RUN][OK] Результати Google Lens для фрагмента '{fragment_name}' збережено: {fragment_lens_filename}")
                    else:
                        LENS_FRAGMENTS_RESULTS[fragment_name] = {"uploaded_url": fragment_url, "lens_data": {"error": "Lens search failed for fragment"}}
                        print(f"[RUN][Warning] Пошук Google Lens для фрагмента '{fragment_name}' не вдався.")
                else:
                    LENS_FRAGMENTS_RESULTS[fragment_name] = {"uploaded_url": None, "lens_data": {"error": "Fragment upload failed"}}
                    print(f"[RUN][Warning] Не вдалося завантажити фрагмент '{fragment_name}' на хостинг.")
        else:
            print("[RUN] Не вдалося обрізати фрагменти.")
    else:
        print("[RUN] Координати для обрізання не знайдено в результатах первинного аналізу.")

    secondary_result = conduct_secondary_analysis(IMAGE_PATH, result, fragment_results_directory=OUTPUT_DIR)
    if secondary_result:
        with open(SECONDARY_PATH, "w", encoding="utf-8") as f:
            json.dump(secondary_result, f, indent=2, ensure_ascii=False)
        print("[Step 2] Secondary analysis saved to:", SECONDARY_PATH)
        print("\n[Secondary Analysis Output]\n", json.dumps(secondary_result, indent=2, ensure_ascii=False))
    else:
        print("[Step 2] Secondary analysis failed.")
        exit(1)