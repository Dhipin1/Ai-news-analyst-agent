# AI News “Analyst” Agent – (Option 2)

This repository contains my solution for **Option 2: The “Analyst” Agent (Advanced Automation)**.

The app:

1. Fetches news about **AI startups** from a public source (TechCrunch RSS by default, optional NewsAPI).
2. **De‑duplicates** similar/duplicate articles.
3. Applies a **“hype / information density” filter** to drop low‑value articles.
4. Uses **local HuggingFace transformer models** (LLM-style) to extract structured fields:
   - `company_name`
   - `category`
   - `headline`
   - `summary`
   - `sentiment_score`
   - `is_funding_news`
   - `confidence`
5. Saves the final list to `extracted_news.csv` (and can optionally write to a Google Sheet).

> Note: I use local HuggingFace models instead of a paid LLM API so the solution can run without OpenAI credits or quotas. The architecture is the same as an LLM‑API pipeline, just self‑contained.

---

## 1. Repository Link & Demo

- **GitHub repo (public):**  
  `TODO: https://github.com/<your-username>/ai-news-analyst-agent`

- **Demo video (Loom / YouTube):**  
  `TODO: https://www.loom.com/share/<your-demo-id>`

- **Screenshots:**  
  Included in the `screenshots/` folder:
  - `run_terminal.png` – full pipeline run in terminal.
  - `csv_preview.png` – preview of `extracted_news.csv`.
  - `dedupe_diagram.png` – diagram of the de‑duplication logic.

---

## 2. Project Structure

```text
.
├─ main.py               # Orchestrates the pipeline
├─ fetcher.py            # Fetch articles from RSS / NewsAPI and extract text
├─ deduper.py            # De-duplication logic
├─ hype_filter.py        # "Hype" filter using information density
├─ extractor.py          # Local LLM-based structured extraction (HuggingFace)
├─ output.py             # Save results to CSV / Google Sheets
├─ requirements.txt      # Dependencies
├─ .env.example          # Example environment variables (no secrets)
├─ extracted_news.csv    # Example output from a recent run
├─ screenshots/          # Demo screenshots (optional if using video)
└─ README.md             # This file