# AutoSense Production Deployment Guide

This guide details the architectural and operational steps required to deploy the complete AutoSense platform across multiple runtime environments.

---

## 1. Architectural Separation of Concerns

AutoSense employs a two-tier decoupling strategy:
1. **The Research Big-Data Cluster (HDFS / Sqoop / Hive):**
   - Runs in an isolated Linux runtime (WSL2 Ubuntu or dedicated private cluster).
   - Never exposed to the public internet or production web tier.
   - Outputs aggregated telemetry and materialized analytical summaries.
2. **The Full-Stack Serving Layer (FastAPI + React Dashboard + MySQL / SQLite):**
   - Powered by precomputed analytical caches (`reports/analytics_cache.json`) and live ML prediction models (`models/traditional_ml/*.joblib` and `models/distilbert/`).
   - Serves both dynamic API requests and the interactive React dashboard from a single port (`8000`).

---

## 2. Option A: Local / Desktop Execution (Antigravity & Windows 11)

No Docker or external cluster is required to run the application locally:

```powershell
# 1. Activate Python virtual environment or use system Python
python -m pip install -r requirements.txt

# 2. Run Database Ingestion (Populates 3000 reviews & 9654 aspect annotations)
python -m src.data.ingest_to_db

# 3. Compile Analytics Cache & Benchmarks
python -m src.analytics.analytics_engine
python -m src.evaluation.run_experiments

# 4. Start Full-Stack FastAPI Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive Dashboard:** Open your browser to `http://127.0.0.1:8000/`
- **Swagger Interactive API Docs:** `http://127.0.0.1:8000/docs`
- **Healthcheck Endpoint:** `http://127.0.0.1:8000/health`

---

## 3. Option B: Docker Compose Deployment (Recommended for Servers)

To launch the full production stack with dedicated MySQL 8.0:

```bash
# 1. Build and start containers
docker compose up -d --build

# 2. Verify container health
docker compose ps

# 3. Check application logs
docker compose logs -f autosense_app
```

The database schema in `bigdata/mysql/schema.sql` is automatically mounted and initialized on first boot.

---

## 4. Option C: Cloud PaaS Deployment (Render / Railway / Fly.io / AWS EC2)

1. **Web Service Setup:**
   - Connect the AutoSense GitHub repository.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
2. **Environment Variables:**
   ```ini
   AUTOSENSE_ENV=production
   SECRET_KEY=generate_a_random_32_byte_hex_string
   DATABASE_URL=mysql+pymysql://<user>:<password>@<db-host>:3306/autosense_db
   ```
3. **Database:**
   - Use managed MySQL (Aiven, PlanetScale, Railway MySQL, or AWS RDS).
   - Execute `bigdata/mysql/schema.sql` via MySQL client.

---

## 5. Security & Governance Checklist

- [x] All database credentials and JWT secret keys reside strictly in environment variables (`.env`).
- [x] `.env` is listed in `.gitignore` and excluded from version control.
- [x] Passwords hashed using standard cryptographic algorithms (`hashlib.sha256` / `bcrypt`).
- [x] No private Hadoop or HDFS ports exposed publicly.
- [x] Strict CORS origin policies configurable in `backend/app/main.py`.
