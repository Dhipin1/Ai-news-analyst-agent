# main.py
from dotenv import load_dotenv

# Load .env BEFORE importing modules that read env vars
load_dotenv()

from fetcher import fetch_from_newsapi, fetch_from_rss, canonicalize_url
from deduper import deduplicate_articles
from hype_filter import is_informative
from extractor import extract_structured
from output import save_to_csv, save_to_gsheet


def run_one_cycle(
    source: str = "newsapi",
    query: str = "AI startups",
    rss_url: str | None = None,
    out_csv: str = "extracted_news.csv",
    use_gsheet: bool = False,
):
    # 1. Fetch
    if source == "newsapi":
        print("Fetching from NewsAPI...")
        articles = fetch_from_newsapi(query=query, page_size=30)
    else:
        print("Fetching from RSS...")
        if not rss_url:
            raise ValueError("rss_url must be provided when source='rss'")
        articles = fetch_from_rss(rss_url)

    print(f"Fetched {len(articles)} items")

    # 2. Canonicalize URLs
    for a in articles:
        a["url"] = canonicalize_url(a.get("url"))

    # 3. De-duplicate
    deduped = deduplicate_articles(articles)
    print(f"After deduplication: {len(deduped)} items")

    # 4. Hype / information-density filter
    informative = [a for a in deduped if is_informative(a.get("text", ""))]
    print(f"After hype filter: {len(informative)} items kept")

    # 5. Structured extraction via OpenAI
    extracted = []
    for i, art in enumerate(informative, start=1):
        print(f"Extracting {i}/{len(informative)}: {art.get('title', '')[:80]}")
        try:
            s = extract_structured(art)
            # add provenance
            s["_source_url"] = art.get("url")
            s["_source_title"] = art.get("title")
            s["_source_time"] = art.get("publishedAt")
            extracted.append(s)
        except Exception as e:
            print("Extraction failed:", e)

    # 6. Output
    if extracted:
        save_to_csv(extracted, out_csv)
        if use_gsheet:
            save_to_gsheet(extracted)
    else:
        print("No extracted items to save.")


if __name__ == "__main__":
    run_one_cycle(
        source="rss",
        rss_url="https://techcrunch.com/feed/",
        out_csv="extracted_news.csv",
        use_gsheet=False,
    )