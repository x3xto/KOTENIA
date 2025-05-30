from google import genai
from google.genai import types
import json
from utils import extract_json_block
from config import api_key

class VisualOSINTAnalyzer:
    def __init__(self, model="gemini-2.5-pro-preview-05-06"): # gemini-2.0-flash
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def analyze_image(self, image_path: str) -> dict:
        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    self._get_prompt()
                ]
            )

            raw_text = response.text or ""
            clean_json = extract_json_block(raw_text)
            return json.loads(clean_json)

        except Exception as e:
            print(f"[Error] Analysis failed: {e}")
            return {"error": str(e)}

    def _get_prompt(self) -> str:
        return """
        You are an expert OSINT (Open-Source Intelligence) analyst specializing in visual forensics and contextual analysis. Your mission is to thoroughly examine the provided image, sourced from public domain, to extract maximum actionable intelligence regarding its location and context.
Based on your comprehensive visual analysis, generate a structured report in JSON format with the following keys:
1.  visual_description: Provide a highly detailed and objective description of all visible elements. Include objects, people (general appearance, no PII), attire, visible text, symbols, architectural styles, landscape, and any temporal indicators (time of day, season). Be precise and observant of even subtle details.
2.  extracted_entities_and_keywords: List all key entities (e.g., specific object types, identified brands, organizations, general categories of people). Also, provide a list of relevant keywords that could be utilized for further, targeted open-source investigation. Prioritize unique or distinctive elements.
3.  ocr_text_and_context: Transcribe all visible text accurately. Provide a concise interpretation of the text's meaning and its immediate relevance within the image's context.
4.  geolocation_analysis: Conduct a robust analysis to hypothesize the most probable geographic location(s).
    Reasoning: Explain in detail how various visual cues (e.g., unique architecture, signage, language, vegetation, vehicle types, cultural elements, specific object models, weather, light) combine and synthesize to support your hypotheses. Emphasize the interconnectedness of these clues.
    Specific Hypotheses: Provide the most specific possible location (e.g., country, region, city type) that can be confidently inferred from the visual evidence. If multiple possibilities exist, list them with supporting arguments. Avoid pinpointing exact private addresses.
5.  unique_identifiers_and_osint_value: Identify any truly unique visual identifiers (e.g., specific brand logos, rare object models, distinctive building features). For each, explain its potential value or direction for further OSINT investigation.
6.  contextual_inferences: Offer a concise assessment of the scene's likely context or nature. Make logical inferences about the broader situation or activity depicted, strictly based on the visual evidence.
Ensure your analysis is strictly based on the visual information and general knowledge, maintaining objectivity and avoiding speculation or generation of private/non-public data.
7.  identifier_bounding_boxes: For each key unique visual identifier (like logos, specific text snippets on signs, distinct objects), if possible, provide approximate bounding box coordinates. The coordinates should define a rectangle around the identifier. If precise bounding boxes are not possible, provide a general description of the area occupied by the identifier.
Use this format for coordinates:
    "UNIQUE_IDENTIFIER_NAME_1": {
      "description": "Brief description of what this identifier is.",
      "coordinates": {
        "x_min": "INTEGER_VALUE",
        "y_min": "INTEGER_VALUE",
        "x_max": "INTEGER_VALUE",
        "y_max": "INTEGER_VALUE"
      }
"""