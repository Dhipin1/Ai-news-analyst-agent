# AI News “Analyst” Agent – AI Intern Challenge (Option 2)

This repository contains my solution for **Option 2: The “Analyst” Agent (Advanced Automation)**.

The app builds an automated workflow that:

1. Fetches news about **AI / AI startups** from a public source (TechCrunch RSS by default, optional NewsAPI).
2. **De‑duplicates** near‑duplicate articles (URL, fuzzy title, semantic similarity).
3. Applies a **“hype / information‑density” filter** to remove low‑value / marketing‑only posts.
4. Uses **local HuggingFace transformer models** (LLM‑style) to extract structured fields:
   - `company_name`
   - `category`
   - `headline`
   - `summary`
   - `sentiment_score`
   - `is_funding_news`
   - `confidence`
5. Saves the final list to `extracted_news.csv` (and can optionally write to a Google Sheet).

> I use **local HuggingFace models** instead of a paid LLM API (OpenAI, etc.) so the solution can run without external LLM quotas or billing. The architecture still has a clear “LLM extraction” step, just self‑contained.

---

## 1. Repository & Demo

- **GitHub repo (public):**  
  Replace with your actual repo URL, for example:  
  `https://github.com/Dhipin1/Ai-news-analyst-agent.git`

- **Demo video (Loom / YouTube):**  
  Put the link you share in your submission email here, for example:  
  `https://youtu.be/Z9RWRqy_-h8`

- **Screenshots (if you choose screenshots instead of video):**  
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
├─ deduper.py            # De-duplication logic (URL + fuzzy + semantic)
├─ hype_filter.py        # "Hype" filter using information density
├─ extractor.py          # Local LLM-based structured extraction (HuggingFace)
├─ output.py             # Save results to CSV / Google Sheets
├─ requirements.txt      # Dependencies
├─ .env.example          # Example environment variables (no secrets)
├─ extracted_news.csv    # Example output from a recent run
├─ screenshots/          # Demo screenshots and diagram
│    ├─ run_terminal.png
│    ├─ csv_preview.png
│    └─ dedupe_diagram.png
└─ README.md             # This file
