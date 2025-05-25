import os
import json
import sys
from first_analysis import VisualOSINTAnalyzer
from secondary_analysis import conduct_secondary_analysis
from image_search import lens_search_image
import utils
from image_cropper import crop_image_by_coordinates
from config import serapi_key


def run_full_pipeline(image_path: str):
    OUTPUT_DIR = "output"
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, "first_result.json")
    SECONDARY_PATH = os.path.join(OUTPUT_DIR, "secondary_result.json")
    CROPPED_FRAGMENTS_DIR = os.path.join(OUTPUT_DIR, "cropped_fragments")
    LENS_FRAGMENTS_RESULTS = {}

    print("[RUN] Starting full analysis pipeline")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    analyzer = VisualOSINTAnalyzer()
    result = analyzer.analyze_image(image_path)

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
    if parsed_coordinates:
        print(f"[RUN] Parsed {len(parsed_coordinates)} bounding boxes for fragments.")
        local_fragment_paths = crop_image_by_coordinates(
            image_path,
            parsed_coordinates,
            CROPPED_FRAGMENTS_DIR
        )

        if local_fragment_paths:
            print(f"[RUN] Cropped and saved {len(local_fragment_paths)} fragments to: {CROPPED_FRAGMENTS_DIR}")
            for fragment_name, fragment_path in local_fragment_paths.items():
                print(f"\n[RUN] Processing fragment: {fragment_name} ({fragment_path})")
                fragment_url = utils.upload_image_get_url(fragment_path)
                if fragment_url:
                    print(f"[RUN] Fragment '{fragment_name}' uploaded to: {fragment_url}")
                    print(f"[RUN] Running Google Lens search for fragment '{fragment_name}'...")
                    lens_results_fragment = lens_search_image(fragment_url, serapi_key, country="")
                    fragment_lens_filename = os.path.join(
                        OUTPUT_DIR,
                        f"lens_fragment_{fragment_name.replace(' ', '_')}.json"
                    )
                    if lens_results_fragment:
                        LENS_FRAGMENTS_RESULTS[fragment_name] = {
                            "uploaded_url": fragment_url,
                            "lens_data": lens_results_fragment
                        }
                        with open(fragment_lens_filename, "w", encoding="utf-8") as f:
                            json.dump(lens_results_fragment, f, indent=2, ensure_ascii=False)
                        print(f"[RUN][OK] Saved Google Lens results for fragment '{fragment_name}': {fragment_lens_filename}")
                    else:
                        LENS_FRAGMENTS_RESULTS[fragment_name] = {"uploaded_url": fragment_url, "lens_data": {"error": "Lens search failed"}}
                        print(f"[RUN][Warning] Google Lens search failed for fragment '{fragment_name}'.")
                else:
                    LENS_FRAGMENTS_RESULTS[fragment_name] = {"uploaded_url": None, "lens_data": {"error": "Upload failed"}}
                    print(f"[RUN][Warning] Failed to upload fragment '{fragment_name}'.")
        else:
            print("[RUN] Failed to crop fragments.")
    else:
        print("[RUN] No bounding box coordinates found in analysis.")

    secondary_result = conduct_secondary_analysis(
        image_path,
        result,
        fragment_results_directory=OUTPUT_DIR
    )
    if secondary_result:
        with open(SECONDARY_PATH, "w", encoding="utf-8") as f:
            json.dump(secondary_result, f, indent=2, ensure_ascii=False)
        print("[Step 2] Secondary analysis saved to:", SECONDARY_PATH)
        print("\n[Secondary Analysis Output]\n", json.dumps(secondary_result, indent=2, ensure_ascii=False))
    else:
        print("[Step 2] Secondary analysis failed.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <image_path>")
        sys.exit(1)
    run_full_pipeline(sys.argv[1])