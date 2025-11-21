# deduper.py
from typing import List, Dict
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def title_fuzzy_equals(t1: str, t2: str, thresh: int = 85) -> bool:
    if not t1 or not t2: return False
    return fuzz.token_set_ratio(t1, t2) >= thresh

def embed_texts(texts: List[str]):
    embs = EMB_MODEL.encode(texts, convert_to_numpy=True)
    # normalize
    faiss.normalize_L2(embs)
    return embs

def semantic_dedup(existing_texts: List[str], candidate_text: str, sim_threshold: float = 0.78) -> bool:
    """
    Returns True if candidate is semantically similar to any existing text.
    sim_threshold ~ cosine similarity threshold (0-1).
    """
    if not existing_texts:
        return False
    all_texts = existing_texts + [candidate_text]
    embs = embed_texts(all_texts)
    # last vector compared to earlier ones
    q = embs[-1]
    pool = embs[:-1]
    sims = (pool @ q).tolist()  # since normalized, dot = cosine
    max_sim = max(sims) if sims else 0.0
    return max_sim >= sim_threshold

def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    """
    Input: list of article dicts (title,url,text,...)
    Output: deduplicated list, keeping first seen in group.
    """
    kept = []
    texts = []  # used for semantic check
    for art in articles:
        # 1) canonical URL duplicate
        url = art.get("url")
        if any((existing.get("url") and existing.get("url").split('?')[0] == (url or "").split('?')[0]) for existing in kept):
            continue
        # 2) fuzzy title duplicate
        if any(title_fuzzy_equals(art.get("title",""), existing.get("title","")) for existing in kept):
            continue
        # 3) semantic duplicate based on text
        if art.get("text"):
            if semantic_dedup([e.get("text","") for e in kept if e.get("text")], art["text"]):
                continue
        # keep
        kept.append(art)
    return kept
