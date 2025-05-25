# KOTENIA

```
 ,_     _
 |\\_,-~/
 / _  _ |    ,--.
(  @  @ )   / ,-'       KOTENIA
 \  _T_/-._( (
 /         `. \        Key Object & Text Extraction, Networking, and Integrated Analytics
|         _  \ |
 \ \ ,  /      |
  || |-_\__   / 
 ((_/`(____,-'
```

**KOTENIA** stands for **Key Object & Text Extraction, Networking, and Integrated Analytics**. This Proof of Concept (PoC) is developed as part of a bachelor's thesis project, demonstrating an end-to-end OSINT pipeline for visual intelligence analysis.

## Features

* **Image Analysis:** Leverages a large vision-language model to extract detailed descriptions, entities, OCR text, and geolocation hypotheses from input images.
* **Fragment Extraction:** Automatically crops and uploads key visual fragments (logos, signs, text) for reverse image searches.
* **Networking & Search:** Integrates with Google Lens (or similar) to enrich analysis with open-source data.
* **Structured Summaries:** Aggregates all results and synthesizes a concise intelligence report in JSON format.
* **Terminal UI:** Provides a rich terminal interface with animated ASCII art and formatted tables for easy readability.

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/x3xto/KOTENIA.git
   cd KOTENIA
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**

   * Copy `config_example.py` to `config.py`
   * Insert your `api_key` (for Gemini) and `serapi_key` (SerpAPI for Google Lens search)

4. **Run the pipeline**

   ```bash
   python summary.py <path_to_image>
   ```

   * The program will clear the `output/` folder, process the image, and save `output/summary.json`.
   * View the formatted summary directly in your terminal.
