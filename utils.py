import re
import json
from typing import Optional

def extract_json_block(text: str) -> str:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_country_code_from_secondary_result(secondary_result: dict) -> str | None:
    if not secondary_result:
        return None
    hypotheses = secondary_result.get("new_location_hypotheses", [])
    for h in hypotheses:
        code = h.get("predicted_country_code")
        if code:
            return code.lower()
    return None