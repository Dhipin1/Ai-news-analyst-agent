# fetcher.py
import os
import requests
import feedparser
from newspaper import Article
from typing import List, Dict, Optional
from urllib.parse import urlparse

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def fetch_from_newsapi(query: str = "AI startups", page_size: int = 20) -> List[Dict]:
    """
    Fetch top articles from NewsAPI.
    Each returned item: {"title","url","source","publishedAt","raw_html","text"}
    """
    if not NEWSAPI_KEY:
        raise RuntimeError("NEWSAPI_KEY not set in environment")
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "pageSize": page_size, "sortBy": "publishedAt", "language": "en", "apiKey": NEWSAPI_KEY}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = []
    for a in data.get("articles", []):
        items.append({
            "title": a.get("title") or "",
            "url": a.get("url"),
            "source": a.get("source", {}).get("name"),
            "publishedAt": a.get("publishedAt"),
            "raw": a
        })
    # Extract article text with newspaper
    for it in items:
        try:
            art = Article(it["url"])
            art.download()
            art.parse()
            it["text"] = art.text
        except Exception:
            it["text"] = ""
    return items

def fetch_from_rss(rss_url: str, max_items: int = 20) -> List[Dict]:
    feed = feedparser.parse(rss_url)
    items = []
    for entry in feed.entries[:max_items]:
        url = entry.get("link")
        title = entry.get("title", "")
        items.append({"title": title, "url": url, "source": feed.feed.get("title",""), "publishedAt": entry.get("published",""), "raw": entry})
    # extract text
    for it in items:
        try:
            art = Article(it["url"])
            art.download()
            art.parse()
            it["text"] = art.text
        except Exception:
            it["text"] = ""
    return items

def canonicalize_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
