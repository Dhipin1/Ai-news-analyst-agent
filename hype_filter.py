# hype_filter.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure required NLTK data is available
def _ensure_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)

_ensure_nltk_data()

STOPWORDS = set(stopwords.words("english"))


def information_density(text: str) -> float:
    if not text:
        return 0.0
    tokens = [t.lower() for t in word_tokenize(text) if re.match(r"\w+", t)]
    total = len(tokens)
    if total == 0:
        return 0.0
    unique = len(set(tokens))
    density = unique / total
    return density


def is_informative(text: str, min_tokens: int = 80, density_thresh: float = 0.28) -> bool:
    if not text:
        return False

    tokens = [t for t in word_tokenize(text) if re.match(r"\w+", t)]
    if len(tokens) < min_tokens:
        return False

    dens = information_density(text)
    if dens < density_thresh:
        return False

    # require some named-like words (capitalized) or digits
    if re.search(r"[A-Z][a-z]{2,}", text) or re.search(r"\d{2,}", text):
        return True

    # fallback: slightly higher density requirement
    return dens >= (density_thresh + 0.05)