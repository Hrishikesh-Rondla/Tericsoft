"""
TF-IDF retrieval over the 12-product Northwind Cloud knowledge base.

WHY TF-IDF INSTEAD OF EMBEDDINGS:
  - Deterministic: same query always returns the same result, making it easy
    to debug and explain in a technical review.
  - Zero latency: the index is built once at import time in < 10 ms; every
    search is a local matrix multiply with no network round-trip.
  - No extra API dependency: embeddings would require a second provider call
    (or a local model), adding cost, failure modes, and setup complexity.
  - Adequate for a 12-document corpus: TF-IDF term overlap is sufficient when
    the vocabulary is controlled and queries use product-domain words.

EXPLICIT TRADEOFF:
  - TF-IDF has NO synonym or semantic matching. A query about "login" will not
    match documents containing only "authentication" or "SSO" unless those
    exact tokens appear. For a 12-doc corpus this is acceptable; for a larger
    or more ambiguous corpus, sentence-transformer embeddings would be better.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.knowledge_base import PRODUCTS

# ---------------------------------------------------------------------------
# Build TF-IDF index at import time (runs once, deterministic).
# We concatenate every text field so that any token in name / description /
# features / ideal_for can be matched by a query.
# ---------------------------------------------------------------------------

def _doc_text(entry: dict) -> str:
    """Flatten all text fields into one string for TF-IDF indexing."""
    features = " ".join(entry["key_features"])
    return (
        f"{entry['name']} {entry['category']} "
        f"{entry['description']} {features} {entry['ideal_for']}"
    )


_corpus = [_doc_text(p) for p in PRODUCTS]
_vectorizer = TfidfVectorizer(stop_words="english")
_tfidf_matrix = _vectorizer.fit_transform(_corpus)  # shape: (12, vocab_size)

FLOOR_SCORE = 0.05  # below this, results are considered low-confidence


def search(query: str, k: int = 3) -> list[dict]:
    """
    Return the top-k products most relevant to *query*.

    Each returned dict is the original PRODUCTS entry plus two extra keys:
      - relevance_score: float in [0, 1], rounded to 4 dp
      - low_confidence: bool – True when NO result cleared FLOOR_SCORE

    If nothing clears the floor, the top-2 results are returned and
    low_confidence is set to True on every result.
    """
    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _tfidf_matrix)[0]  # shape: (12,)

    # Pair each product with its score, sort descending
    ranked = sorted(
        zip(scores, PRODUCTS), key=lambda t: t[0], reverse=True
    )

    # Check whether ANY result clears the floor
    any_above_floor = any(score >= FLOOR_SCORE for score, _ in ranked[:k])

    if any_above_floor:
        selected = [(score, p) for score, p in ranked[:k] if score >= FLOOR_SCORE]
        low_confidence = False
    else:
        # Nothing cleared the floor – return top-2 and flag it
        selected = ranked[:2]
        low_confidence = True

    results = []
    for score, product in selected:
        entry = dict(product)  # shallow copy so we don't mutate PRODUCTS
        entry["relevance_score"] = round(float(score), 4)
        entry["low_confidence"] = low_confidence
        results.append(entry)

    return results
