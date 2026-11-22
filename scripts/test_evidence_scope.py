import sys, os
sys.path.insert(0, os.path.abspath('.'))
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

res = client.get("/api/evidence?scope=all&target=all&limit=5")
print("Status with scope=all:", res.status_code)
data = res.json()
print("Total reviews:", data.get("total_reviews"))
print("First review:", data.get("evidence_reviews", [{}])[0].get("review_text", "")[:80])

res2 = client.get("/api/evidence?scope=brand&target=Toyota&limit=3")
print("Status with brand=Toyota:", res2.status_code)
data2 = res2.json()
print("Toyota reviews count:", data2.get("total_reviews"))
