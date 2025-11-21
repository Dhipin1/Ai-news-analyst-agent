# extractor.py  -- LOCAL version, NO OpenAI/paid API needed
from typing import Dict, Optional

from transformers import pipeline

# Lazy-loaded pipelines (initialized on first use)
_NER_PIPE = None
_SENTIMENT_PIPE = None
_SUMMARIZER_PIPE = None
_ZSHOT_PIPE = None


def _init_pipelines() -> None:
    """
    Load all required HuggingFace models.
    This may take a few minutes the first time (model download).
    """
    global _NER_PIPE, _SENTIMENT_PIPE, _SUMMARIZER_PIPE, _ZSHOT_PIPE

    if _NER_PIPE is not None:
        return

    print("Loading local NLP models (first run can take several minutes)...")

    # Named-entity recognition: to find company / organization names
    _NER_PIPE = pipeline(
        "ner",
        model="dslim/bert-base-NER",
        grouped_entities=True,
    )

    # Sentiment analysis: to get sentiment_score
    _SENTIMENT_PIPE = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )

    # Summarization: to create a short factual summary
    _SUMMARIZER_PIPE = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
    )

    # Zero-shot classification: to decide category
    _ZSHOT_PIPE = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
    )


def _clean(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.replace("\n", " ").split()).strip()


def _extract_company_name(text: str) -> Optional[str]:
    try:
        entities = _NER_PIPE(text[:512])
    except Exception as e:
        print("NER error:", e)
        return None

    orgs = [e for e in entities if e.get("entity_group") == "ORG"]
    if not orgs:
        return None

    # Return the first organization detected
    return orgs[0].get("word")


def _summarize_text(text: str, title: str) -> str:
    base = text or title
    if not base:
        return ""

    try:
        # Summarization models like this accept ~1024 tokens; we clip by characters.
        chunk = base[:4000]
        result = _SUMMARIZER_PIPE(
            chunk,
            max_length=120,
            min_length=40,
            do_sample=False,
        )[0]
        return result["summary_text"]
    except Exception as e:
        print("Summarization error:", e)
        # Fallback: first 2–3 sentences
        import re

        sents = re.split(r"(?<=[.!?])\s+", base)
        return " ".join(sents[:3])


def _classify_category(text: str) -> str:
    labels = ["AI", "Funding", "Product", "M&A", "Policy/Regulation", "Research", "Other"]
    try:
        res = _ZSHOT_PIPE(
            text[:512],
            candidate_labels=labels,
            multi_label=False,
        )
        if "labels" in res and res["labels"]:
            return res["labels"][0]
    except Exception as e:
        print("Zero-shot classification error:", e)
    return "Other"


def _compute_sentiment_score(text: str) -> float:
    try:
        res = _SENTIMENT_PIPE(text[:512])[0]
        label = res["label"].upper()
        score = float(res["score"])

        if label == "POSITIVE":
            val = 0.5 + score / 2.0
        elif label == "NEGATIVE":
            val = 0.5 - score / 2.0
        else:
            val = 0.5
    except Exception as e:
        print("Sentiment error:", e)
        val = 0.5

    # Clamp to [0,1]
    return max(0.0, min(val, 1.0))


def extract_structured(article: Dict) -> Dict:
    """
    Drop-in replacement for the old OpenAI-based extract_structured().
    Uses only local HuggingFace models.

    Returns a dict with:
      - company_name
      - category
      - headline
      - summary
      - sentiment_score
      - is_funding_news
      - confidence
    """
    _init_pipelines()

    text = _clean(article.get("text", ""))
    title = _clean(article.get("title", ""))
    url = article.get("url") or ""

    combined = (title + ". " + text).strip()

    # 1) Summary
    summary = _summarize_text(text, title)

    # 2) Company name (ORG from NER)
    company_name = _extract_company_name(combined)

    # 3) Category via zero-shot classification
    category_input = (title + ". " + summary).strip()
    category = _classify_category(category_input)

    # 4) Sentiment score
    sentiment_score = round(_compute_sentiment_score(combined), 3)

    # 5) Funding news detection
    lower_all = combined.lower()
    funding_keywords = [
        "raises ",
        "raised ",
        "raising ",
        "funding",
        "seed round",
        "series a",
        "series b",
        "series c",
        "series d",
        "series e",
        "pre-seed",
        "pre seed",
        "valuation",
        "invests in",
        "investment",
        "investors",
        "financing round",
        "equity round",
    ]
    is_funding_news = category == "Funding" or any(kw in lower_all for kw in funding_keywords)

    # 6) Simple confidence heuristic
    confidence = 0.6
    if company_name:
        confidence += 0.1
    if summary:
        confidence += 0.1
    confidence = min(confidence, 1.0)

    return {
        "company_name": company_name,
        "category": category,
        "headline": title,
        "summary": summary,
        "sentiment_score": sentiment_score,
        "is_funding_news": bool(is_funding_news),
        "confidence": round(confidence, 2),
    }