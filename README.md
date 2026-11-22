# AutoSense: Big Data Sentiment Analysis for the Automobile Industry using Apache Sqoop

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Apache Sqoop](https://img.shields.io/badge/Apache%20Sqoop-1.4.7-red.svg)](https://sqoop.apache.org/)
[![Hadoop HDFS](https://img.shields.io/badge/Apache%20Hadoop-3.3-yellow.svg)](https://hadoop.apache.org/)
[![License: Academic Research](https://img.shields.io/badge/License-Research%20%26%20Competition-purple.svg)]()

> **AutoSense** is an end-to-end big-data and machine-learning intelligence platform for the automotive industry. It collects structured customer reviews across manufacturers, ingests them from relational storage (MySQL) into distributed storage (Hadoop HDFS) via Apache Sqoop, processes and normalizes multi-aspect opinions through Hive, and trains comparative NLP models (Linear SVM, Logistic Regression, Naive Bayes, DistilBERT, and VADER) to surface evidence-backed customer sentiment, 8-aspect ABSA opinions, and complaint hotspots.

---

## 1. System Architecture & Logical Data Flow

```
+---------------------------------------------------------------------------------------------------+
|                                  AUTOSENSE ARCHITECTURAL PIPELINE                                  |
+---------------------------------------------------------------------------------------------------+

 [ Automobile Reviews ]       [ Hybrid Car ABSA ]        [ MuSe-CarASTE ]          [ Edmunds Reviews ]
 (15,000 DB / 12,000 Curated) (1,002 Peer-Reviewed)      (28,295 Sentences)        (13,790 Reviews)
           |                          |                           |                         |
           +--------------------------+---------------------------+-------------------------+
                                      |
                                      v
                      +-------------------------------+
                      |   MySQL Relational Database   |
                      |   (autosense_local.db / SQLite|
                      |    & MySQL production schema) |
                      +-------------------------------+
                                      |
                                      |  Apache Sqoop 1.4.7
                                      |  (113,145 records/sec SIMULATED throughput)
                                      v
                      +-------------------------------+
                      |   Hadoop Distributed HDFS     |
                      |   (/autosense/hdfs/raw_reviews)
                      |   128 MB Blocks / 3x Replicas |
                      +-------------------------------+
                                      |
                                      |  Apache Hive External Tables
                                      v
                      +-------------------------------+
                      |   Apache Hive Data Warehouse  |
                      |   (Aggregations & Analytics)  |
                      +-------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------------------------+
|                                   DATA CLEANING & ML MODELLING                                    |
|   src/preprocessing/text_cleaner.py  -->  Negation & Vehicle Specification Preservation           |
|   Stratified Leak-Free Splits        -->  Train (10,500 / 70%) | Val (2,250 / 15%) | Test (2,250) |
+---------------------------------------------------------------------------------------------------+
        |                         |                         |                        |
        v                         v                         v                        v
  [ Model 1: Linear SVM ]   [ Model 2: Logistic Reg ] [ Model 3: Naive Bayes ] [ Model 4: DistilBERT ]
   (Top Performer - 93.0%)   (Calibrated - 92.8%)      (Multinomial - 92.3%)    (Transformer - 64.2%)
        |                         |                         |                        |
        +-------------------------+-------------------------+------------------------+
                                  |
                                  v
                  +-------------------------------+
                  |    AutoSense Analytics Engine |
                  |    8-Aspect ABSA Triplet Ext. |
                  |    Complaint Hotspot Detection|
                  +-------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|                                  FULL-STACK SERVING & USER INTERFACE                              |
|   FastAPI Backend (Port 8000)  <=================>  Interactive Web Dashboard (index.html)        |
|   - /                                               - Overview & KPIs (15,000 Reviews)            |
|   - /api/evidence (Corpus / Brand / Model / Aspect) - 15-Brand Comparative Analytics              |
|   - /api/predict & /api/predict/compare             - 57 Vehicle Models Drill-Down with Real Photos|
|   - /api/predict/batch (25 Reviews Parallel)        - Locked 8-Aspect ABSA Taxonomy Matrix        |
|   - /api/dashboard & /api/research                  - 5-Model Comparison Lab + Live Predictor     |
|   - /api/chat (Automotive NLP Copilot)              - Sqoop & HDFS Animated Big Data Telemetry    |
|                                                     - Dataset Center + Preprocessing Pipeline Flow|
|                                                     - Light / Dark Theme Toggle + Auth Personas   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Experimental Benchmark Summary

Evaluated on the held-out test split (2,250 reviews, zero data leakage, seed 42):

| Model Version | Architecture | Test Accuracy | Macro F1 | Weighted F1 | Latency | Purpose |
|---|---|---|---|---|---|---|
| `autosense-tfidf-svm-v1` | **Linear SVM (Max-Margin)** | **93.00%** | **0.9088** | **0.9290** | **74 ms** | **Production Top Performer** |
| `autosense-tfidf-lr-v1` | TF-IDF + Logistic Regression | **92.84%** | **0.9065** | **0.9273** | **125 ms** | Calibrated Probabilistic Baseline |
| `autosense-tfidf-nb-v1` | TF-IDF + Multinomial Naive Bayes | **92.27%** | **0.9021** | **0.9195** | **63 ms** | Ultra-Fast Classical Baseline |
| `autosense-vader-baseline-v1` | VADER (Rule-Based Lexicon) | **67.82%** | **0.4986** | **0.6243** | **1 ms** | Unsupervised Baseline |
| `autosense-distilbert-v1` | Fine-Tuned DistilBERT | **64.22%** | **0.3089** | **0.5187** | **115 ms** | Transformer Sequence Classifier |

### Locked 8-Aspect ABSA Taxonomy & Empirical F1

Evaluated against 27,778 aspect-opinion triplets from MuSe-CarASTE & Manzoor 2022:

| Aspect Category | Subcategories | Precision | Recall | F1-Score | Evaluated Triplets |
|---|---|---|---|---|---|
| **Performance** | Engine, acceleration, braking, handling, transmission | 0.728 | 0.701 | **71.4%** | 7,220 |
| **Economy** | Mileage, fuel consumption, running cost | 0.754 | 0.712 | **73.2%** | 2,854 |
| **Comfort** | Seats, legroom, suspension, cabin space | 0.695 | 0.684 | **68.9%** | 5,320 |
| **Technology** | Infotainment, navigation, Bluetooth, connectivity | 0.662 | 0.629 | **64.5%** | 987 |
| **Safety** | Airbags, ABS, ADAS, safety rating | 0.718 | 0.685 | **70.1%** | 3,289 |
| **Design** | Interior, exterior, paint, styling | 0.688 | 0.668 | **67.8%** | 4,351 |
| **Ownership** | Service, maintenance, reliability, spare parts | 0.645 | 0.620 | **63.2%** | 1,444 |
| **Value** | Price, features, resale value | 0.710 | 0.687 | **69.8%** | 1,913 |
| **Overall ABSA** | **Combined 8-Aspect System** | **0.700** | **0.683** | **69.13%** | **27,778** |

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.11+
- Windows PowerShell / Linux Bash

### Installation
```powershell
# Navigate to the workspace
cd V:\BDT

# Install dependencies
pip install -r requirements.txt
```

### Server Execution & Port Troubleshooting

> **IMPORTANT:** Always check if the server is already running before starting a new instance.
> If port 8000 is occupied, you will see `[WinError 10013]` or `[WinError 10048]`.

#### 1. Check if the server is already running:
```powershell
netstat -ano | findstr ":8000"
```
If you see `LISTENING`, the server is **already active and serving traffic**. You do not need to run `uvicorn` again! Open your browser directly.

#### 2. Start the server (if NOT already running):
```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Open **http://127.0.0.1:8000/** in your browser.

#### 3. If port 8000 is blocked by an old ghost process:
```powershell
# Kill existing Python uvicorn processes
taskkill /F /IM python.exe

# Wait 3 seconds, then start cleanly
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
or
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Access via DevTunnel (Remote / Cloud Forwarding):
```
https://xlqzr0rt-8000.inc1.devtunnels.ms/
```
The DevTunnel forwards port `8000` to the internet. When the server is running on `127.0.0.1:8000`, the DevTunnel link works automatically.

### Running Automated Test Suite
```powershell
python -m unittest tests/test_end_to_end.py -v
```
**Result:** 15/15 tests passing (0.59s).

---

## 4. Key Platform Features

### A. Login & Persona Switcher
- **4 Active Personas:**
  - ⚡ **Demo Mode** (`demo@gmail.com`): Interactive exploration & sandbox
  - 👔 **Executive View** (`executive@autosense.ai`): Brand satisfaction & strategic KPIs
  - 📊 **Data Analyst View** (`analyst@autosense.ai`): Multi-graph trends, aspect drill-downs
  - 🔬 **Researcher View** (`researcher@autosense.ai`): Scientific benchmarks, confusion matrices, MuSe-CarASTE ground truth
- **Create Account Tab:** Full sign-up flow storing persistent credentials in `localStorage`

### B. Theme Switcher (☀️ Light Mode / 🌙 Dark Mode)
- One-click toggle in top header (`#theme-toggle-btn`)
- Comprehensive CSS theme engine with full palette inversion
- Persists user selection automatically in `localStorage('autosense_theme')`

### C. 🚗 Vehicle Model Drill-Down
- 57 vehicle models across 15 manufacturers
- Every model card features high-resolution photography with hover zoom
- Filter by manufacturer or search by model name (Thar, Safari, Hycross, Creta, etc.)
- Deep detail view with aspect scores, sentiment breakdown, and verified review stream

### D. 🔍 Evidence Explorer Modal
- Query the raw 15,000-review database with aspect-opinion triplets
- Scopes: Entire Corpus (`scope=all`), Brand (`scope=brand`), Model, Aspect
- Filter reviews by All, Positive Only, or Negative Complaints
- Verifiable evidence grounding with zero synthetic hallucinations

### E. ⚡ 5-Model Comparison Lab
- Live parallel evaluation across 5 distinct architectures:
  1. Linear SVM (Production Max-Margin)
  2. Logistic Regression (Calibrated Probabilities)
  3. Multinomial Naive Bayes (Frequency-based)
  4. VADER Lexicon Analyzer (Unsupervised)
  5. Fine-Tuned DistilBERT (Contextual Transformer)
- Displays consensus sentiment, model agreement %, aspect detection chips, and per-model latency (ms)

### F. 📊 25-Review Batch Evaluation
- Evaluates 25 stratified automotive reviews in parallel
- Displays benchmark accuracy, processing latency, and brand distribution
- Generates 3 prioritized engineering recommendations with identified root causes
- Interactive review cards stream for deep review inspection

### G. 🔧 Animated Preprocessing Pipeline Flow
- Step 1: Raw Multi-Source Ingestion
- Step 2: HTML & Noise Stripping
- Step 3: Contraction Expansion
- Step 4: Negation Preservation (`not_good`, `won't_start`)
- Step 5: Vehicle Spec Token Filtering (`abs`, `adas`, `nvh`, `bhp`, `mpg`)
- Step 6: Stratified Leak-Free Split (70/15/15)
- Live before-and-after text sanitization examples

---

## 5. Repository Structure

```
AutoSense/
├── backend/app/            # FastAPI REST backend (routes, schemas, auth, main.py)
│   ├── main.py             # Server entrypoint with static file serving & CORS
│   └── routes/api.py       # Evidence, prediction, batch, and analytics endpoints
├── bigdata/                # MySQL DDL, Apache Sqoop scripts, HDFS setup, Hive DDL, logs
│   ├── mysql/              # Database dump & autosense_local.db SQLite database
│   ├── sqoop/              # Sqoop import scripts, telemetry logs, and architecture
│   ├── hdfs/               # Hadoop distributed file system mapping specifications
│   └── hive/               # Hive schema definitions & external table DDL
├── Datasets/               # Raw, normalized, and stratified splits (train/val/test)
├── frontend/dist/          # Production Single-Page Dashboard
│   ├── index.html          # Complete SPA with dark/light themes and 10 views
│   ├── autosense_bundle.json # Pre-computed research analytics & review corpus
│   └── models_catalog.json # 57 vehicle models with photography metadata
├── models/                 # Versioned model artifacts (Joblib & DistilBERT weights)
├── reports/                # Analytical cache, research summaries, and EDA reports
├── src/                    # Data ingestion, text cleaning, models, analytics engine
├── tests/                  # Automated unit and integration test suites
│   └── test_end_to_end.py  # 15 comprehensive end-to-end test cases
├── requirements.txt        # Pinned Python dependencies
└── README.md               # Complete platform documentation
```
