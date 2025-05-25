import subprocess
import os
import json
import sys
import shutil
from google import genai
from config import api_key
from utils import extract_json_block
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

client = genai.Client(api_key=api_key)
console = Console()
ASCII_ART = r"""
 ,_     _
 |\\_,-~/
 / _  _ |    ,--.
(  @  @ )   / ,-'
 \  _T_/-._( (
 /         `. \
|         _  \ |  KOTENIA initialized
 \ \ ,  /      |
  || |-_\__   /  Please wait..
 ((_/`(____,-'
"""

def call_run_and_capture(image_path: str) -> str:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "run.py", image_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="ignore",
        env=env
    )
    out = result.stdout or ""
    err = result.stderr or ""
    return out + "\n" + err


def summarize_via_gemini(raw_output: str) -> dict:
    prompt = f"""
You are acting as an expert OSINT-focused summarizer. You will be given the full raw output from an automated visual OSINT pipeline (including logs, parsed JSON blocks, and fragment search results).

Your task is to:
1. Parse and extract relevant structured data embedded in the output.
2. Aggregate this data into one cohesive laconical intelligence report.
3. Return the report strictly in valid JSON format with this schema:
{{
  "visual_description": "Concise description of the scene.",
  "entities": {{ "persons": [], "organizations": [], "flags": [], "symbols": [], "vehicles": [], "other": [] }},
  "keywords": [],
  "geolocation_analysis": {{
    "probable_location": "Most confident location",
    "justification": "Summary of reasoning combining all data"
  }},
  "osint_identifiers": [{{ "id": "", "description": "", "osint_value": "" }}],
  "inference": "High-level scenario inference",
  "source_links": [{{ "object": "", "link": "", "lens_results": "" }}]
}}

Raw pipeline output:
```
{raw_output}
```
Return only the JSON."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    json_text = response.text or ""
    json_block = extract_json_block(json_text)
    return json.loads(json_block)


def print_pretty(summary: dict) -> None:
    console.print(Panel(summary.get("visual_description", ""), title="Visual Description",  box=box.ROUNDED, expand=True))
    ents = summary.get("entities", {})
    table = Table(title="Entities", box=box.SIMPLE, expand=True)
    table.add_column("Category", justify="left")
    table.add_column("Items", justify="left")
    for cat, items in ents.items():
        if items:
            table.add_row(cat.capitalize(), ", ".join(items))
    console.print(table)
    console.print(Panel(", ".join(summary.get("keywords", [])), title="Keywords", box=box.ROUNDED, expand=True))
    geo = summary.get("geolocation_analysis", {})
    geo_text = f"Probable Location: {geo.get('probable_location', '')}\nJustification: {geo.get('justification', '')}"
    console.print(Panel(geo_text, title="Geolocation Analysis", box=box.ROUNDED, expand=True))
    ids = summary.get("osint_identifiers", [])
    id_table = Table(title="OSINT Identifiers", box=box.ROUNDED, expand=True)
    id_table.add_column("ID", justify="left")
    id_table.add_column("Description", justify="left")
    id_table.add_column("Value", justify="left")
    for ident in ids:
        id_table.add_row(
            ident.get('id', ''),
            ident.get('description', ''),
            ident.get('osint_value', '')
        )
    console.print(id_table)
    console.print(Panel(summary.get('inference', ''), title="Inference", box=box.ROUNDED, expand=True))
    links = summary.get('source_links', [])
    if links:
        link_table = Table(title="Source Links", box=box.SIMPLE, expand=True)
        link_table.add_column("Object", justify="left")
        link_table.add_column("URL", justify="left")
        link_table.add_column("Lens Results", justify="left")
        for link in links:
            link_table.add_row(
                link.get('object', ''),
                link.get('link', ''),
                link.get('lens_results', '')
            )
        console.print(link_table)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.print("Usage: python summary.py <path_to_image>")
        sys.exit(1)
    shutil.rmtree("output", ignore_errors=True)
    os.makedirs("output", exist_ok=True)
    print(ASCII_ART)
    image_path = sys.argv[1]
    raw = call_run_and_capture(image_path)
    summary = summarize_via_gemini(raw)
    with open(os.path.join("output", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    console.print("Saved summary to output/summary.json")
    print_pretty(summary)
