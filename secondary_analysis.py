import json
from typing import Optional
from google import genai
from google.genai import types
from config import api_key
from utils import extract_json_block

client = genai.Client(api_key=api_key)

def conduct_secondary_analysis_with_gemini(image_path: str, initial_analysis_json: dict) -> Optional[dict]:
    print("\n[Step 2] Secondary analysis with image and JSON.")

    try:
        json_string = json.dumps(initial_analysis_json, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Step 2] Error parsing JSON into a string: {e}")
        return None

    prompt = f"""You are an expert OSINT investigator and a specialist in geographic profiling based on visual and textual clues. Your mission is to synthesize structured data from an initial image examination and formulate specific, testable hypotheses about the image's origin, focusing on pinpointing potential locations. Also consider if there's any words - it can be only a part of a word, without starting or finishing (or both) letters. If there's any symbol present - consider not only heraldry but also famous business logos.

You are also provided with the original image. Use both the image and structured analysis data below to support your reasoning.

Here is the structured JSON output from the initial visual analysis:
{json_string}

Please return a JSON object with the following structure:
{{
  "prime_geolocational_indicators": [...],
  "cross_correlation": {{
    "analysis": "...",
    "refined_hypothesis": "..."
  }},
  "new_location_hypotheses": [
    {{
      "location_hypothesis": "...",
      "predicted_country_code": "2 symbols, like us, ua, ru",
      "confidence": "High | Medium | Low",
      "justification": "...",
      "verification_steps": ["...", "..."]
    }}
  ],
  "intelligence_brief": "...",
  "next_steps": ["...", "..."]
}}"""

    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        model_name = 'gemini-2.0-flash'
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )
        print("[Step 2] Answer from Gemini.")
        return json.loads(extract_json_block(response.text or ""))
    except Exception as e:
        print(f"[Step 2] Error getting response Gemini: {e}")
        return None
