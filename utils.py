import re

def extract_json_block(text: str) -> str:
    """
    Витягує JSON-блок з тексту, обгорнутого в ```json ... ``` або просто повертає trimmed text.
    """
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


# File: visual_extractor.py
from google import genai
from google.genai import types
import os
import json
from config import api_key
from utils import extract_json_block

class VisualOSINTAnalyzer:
    def __init__(self, model="gemini-2.0-flash"):
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
        return """You are an expert OSINT (Open-Source Intelligence) analyst specializing in visual forensics and contextual analysis. Your mission is to thoroughly examine the provided image, sourced from public domain, to extract maximum actionable intelligence..."""

