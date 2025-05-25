import json
from typing import Optional, Dict, List
from pathlib import Path
from google import genai
from google.genai import types
from config import api_key
from utils import extract_json_block, aggregate_fragment_results

client = genai.Client(api_key=api_key)

def conduct_secondary_analysis(
    image_path: str,
    initial_analysis_json: dict,
    fragment_results_directory: str
) -> Optional[dict]:
    print("\n[Step 2] Secondary analysis with image and JSON.")

    fragment_search_results = aggregate_fragment_results(fragment_results_directory)

    try:
        initial_json_string = json.dumps(initial_analysis_json, indent=2, ensure_ascii=False)
        fragments_json_string = json.dumps(fragment_search_results, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Step 2] Error parsing JSON into a string: {e}")
        return None

    prompt = f"""
You are an expert OSINT (Open-Source Intelligence) investigator and a specialist in geographic profiling and data synthesis. Your mission is to meticulously analyze and synthesize structured data derived from an initial visual examination of a publicly sourced image, along with supplementary data obtained from reverse image searches performed on key fragments extracted from that original image. Your goal is to formulate specific, testable hypotheses about the image's origin and context, focusing on pinpointing potential locations and a_c_t_i_o_n_a_b_l_e_ *i_n_t_e_l_l_i_g_e_n_c_e*.

**General analytical considerations:**

- When analyzing text (e.g., from OCR or search snippets), consider that words might be partial, without starting or finishing letters, or even misspelled.
- When analyzing symbols or logos, consider not only heraldry but also well-known business logos or local emblems.

**Input Data:**

**1. Structured JSON output from the initial visual analysis of the entire image:**

{initial_json_string}

**2. JSON array containing results from reverse image searches on specific fragments identified in the initial analysis:**

{fragments_json_string}

Your Comprehensive Analytical Task:

Based on all the provided data (both the initial full image analysis and the fragment search results):

Identify Prime Geolocational Indicators (Synthesized): From both JSON inputs, identify the top 3-5 
individual or combined visual/textual cues that you now believe are MOST critical for geolocation. 
List them and explain why their combination is significant.
Cross-Correlation and Synthesis:
Analyze: How do the reverse_image_search_results for each fragment_identifier (from fragment_search_results_json_array) 
correlate with, confirm, contradict, or add new details to the findings in the initial_image_analysis_json (especially 
geolocation_analysis, ocr_text_and_context, and unique_identifiers_and_osint_value)?
Pay close attention to titles, snippets, and linked pages from the fragment search results.
Refined Hypothesis (Overall Context): Based on this cross-correlation, provide a refined overall hypothesis about the 
original image's context and potential origin.
New Specific Location Hypotheses (Enhanced by Fragment Data):
Based on your comprehensive synthesis (initial analysis + all fragment search results), propose 1-3 NEW or significantly 
REFINED, specific, and plausible geographic location hypotheses for the original image.
For each hypothesis:
location_hypothesis: (e.g., specific city, region, or even type of neighborhood).
predicted_country_code: (A 2-letter ISO country code, e.g., "UA", "IT", "PL").
confidence: ("High" | "Medium" | "Low").
justification: Detailed explanation of how the combined evidence (initial image + fragment search results) supports this specific 
hypothesis. Explicitly mention how fragment search data helped narrow down or confirm aspects.
verification_steps: Concrete, actionable steps or specific search queries a human analyst could perform to verify or refute this hypothesis.
Updated Intelligence Brief (Synthesized):
Provide a concise intelligence brief (max 200 words) summarizing the most critical observations, the strongest synthesized location hypothesis(es) with confidence levels, and key supporting evidence from all provided data sources.
Prioritized Next Steps for Human Analyst:
Based on all findings, provide a prioritized list of 2-3 concrete next steps for a human OSINT analyst to take to further this investigation and verify the top hypotheses.
Output Format:
Return your entire response as a single, valid JSON object with the following exact structure:

{{
  "prime_geolocational_indicators_synthesized": [
    {{"indicator": "...", "combined_significance": "..."}}
  ],
  "cross_correlation_and_synthesis_analysis": {{
    "analysis_of_fragment_searches_in_context_of_initial_image": "...",
    "refined_overall_hypothesis": "..."
  }},
  "new_location_hypotheses_enhanced": [
    {{
      "location_hypothesis": "...",
      "predicted_country_code": "XX",
      "confidence": "High | Medium | Low",
      "justification": "...",
      "verification_steps": ["...", "..."]
    }}
  ],
  "intelligence_brief_synthesized": "...",
  "next_steps_prioritized": ["...", "..."]
}}
Ensure your analysis is objective, strictly based on the provided structured data inputs, and avoids unsupported speculation. Do not introduce external knowledge beyond what's necessary to interpret the given clues (e.g., general knowledge about logo recognition or geographic distribution of certain architectural styles is acceptable if relevant to clues in the provided JSONs).
"""

    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        model_name = 'gemini-2.5-pro-preview-05-06' #gemini-2.0-flash
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
        print(f"[Step 2] Error getting response from Gemini: {e}")
        return None
