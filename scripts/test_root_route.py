import sys, os
sys.path.insert(0, os.path.abspath('.'))
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
res_root = client.get("/")
print("GET / status:", res_root.status_code)
print("GET / content-type:", res_root.headers.get("content-type"))
print("GET / text snippet:", res_root.text[:120])

res_index = client.get("/index.html")
print("GET /index.html status:", res_index.status_code)

res_health = client.get("/health")
print("GET /health status:", res_health.status_code)
