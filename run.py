import os
import json
from visual_extractor import VisualOSINTAnalyzer

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