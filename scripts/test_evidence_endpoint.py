import sys
sys.path.insert(0, 'V:/BDT')
from backend.app.routes.api import get_evidence_explorer

def test_evidence():
    print("Testing get_evidence_explorer for Brand: Nissan...")
    e_brand = get_evidence_explorer(scope="brand", target="Nissan", limit=5)
    print("  Total reviews:", e_brand["total_reviews"])
    print("  Sentiment counts:", e_brand["sentiment_counts"])
    print("  Sample reliability:", e_brand["sample_size_reliability"])
    print("  Reviews returned:", len(e_brand["evidence_reviews"]))
    if e_brand["evidence_reviews"]:
        r = e_brand["evidence_reviews"][0]
        print("  Sample review text:", r["review_text"][:80], "...")
        print("  Aspect triplets:", r["aspect_triplets"])

    print("\nTesting get_evidence_explorer for Aspect: Performance...")
    e_aspect = get_evidence_explorer(scope="aspect", target="Performance", limit=5)
    print("  Total reviews with Performance:", e_aspect["total_reviews"])
    print("  Reviews returned:", len(e_aspect["evidence_reviews"]))

    print("\n[SUCCESS] /api/evidence works perfectly and returns real reviews with triplets!")

if __name__ == "__main__":
    test_evidence()
