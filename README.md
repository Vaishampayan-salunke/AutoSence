# AutoSense: Big Data Sentiment Analysis for the Automobile Industry using Apache Sqoop

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Apache Sqoop](https://img.shields.io/badge/Apache%20Sqoop-1.4.7-red.svg)](https://sqoop.apache.org/)
[![Hadoop HDFS](https://img.shields.io/badge/Apache%20Hadoop-3.3-yellow.svg)](https://hadoop.apache.org/)
[![License: Academic Research](https://img.shields.io/badge/License-Research%20%26%20Competition-purple.svg)]()

> **AutoSense** is an end-to-end big-data and machine-learning intelligence platform for the automotive industry. It collects structured customer reviews across manufacturers, ingests them from relational storage (MySQL) into distributed storage (Hadoop HDFS) via Apache Sqoop, processes and normalizes multi-aspect opinions through Hive, and trains comparative NLP models (VADER, TF-IDF + Logistic Regression, Linear SVM, Naive Bayes, and DistilBERT) to surface evidence-backed customer sentiment and complaint hotspots.

---

## 1. System Architecture & Logical Data Flow

```
+---------------------------------------------------------------------------------------------------+
|                                  AUTOSENSE ARCHITECTURAL PIPELINE                                  |
+---------------------------------------------------------------------------------------------------+

 [ Automobile Reviews ]       [ Hybrid Car ABSA ]        [ Amazon Automotive ]     [ Edmunds Reviews ]
 (3,000 Verified Rows)      (1,002 Peer-Reviewed)         (50,000 Reviews)          (13,790 Reviews)
           |                          |                           |                         |
           +--------------------------+---------------------------+-------------------------+
                                      |
                                      v
                      +-------------------------------+
                      |   MySQL Relational Database   |
                      |   (autosense_db / InnoDB)     |
                      +-------------------------------+
                                      |
                                      |  Apache Sqoop 1.4.7
                                      |  (113,145 records/sec throughput)
                                      v
                      +-------------------------------+
                      |   Hadoop Distributed HDFS     |
                      |   (/autosense/raw/reviews/)   |
                      +-------------------------------+
                                      |
                                      |  Hive External Tables (Tab-delimited)
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
|   Stratified Leak-Free Splits        -->  Train (70%) | Validation (15%) | Test (15%)             |
+---------------------------------------------------------------------------------------------------+
        |                         |                         |                        |
        v                         v                         v                        v
  [ Model 1: VADER ]      [ Model 2: TF-IDF + LR ]  [ Model 3: Linear SVM ]  [ Model 4: DistilBERT ]
   (Rule-Based Lexicon)    (Main Linear Baseline)    (Calibrated Prob.)      (Sequence Transformer)
   Acc: 70.0% | F1: 61.4%  Acc: 100% | F1: 100%       Acc: 100% | F1: 100%     Acc: 59.6% | F1: 42.8%
        |                         |                         |                        |
        +-------------------------+-------------------------+------------------------+
                                  |
                                  v
                  +-------------------------------+
                  |    AutoSense Analytics Engine |
                  |    Complaint Hotspot Detection|
                  +-------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------------------------+
|                                  FULL-STACK SERVING & USER INTERFACE                              |
|   FastAPI Backend (Port 8000)  <=================>  React + Tailwind CSS Interactive Dashboard    |
|   - /api/dashboard                                  - Overview KPIs & Polarity Donut Chart        |
|   - /api/brands & /api/models                       - 8 Brand & 32 Model Matrices                 |
|   - /api/aspects & /api/complaints                  - Complaint Hotspot Ranking with Evidence     |
|   - /api/predict (Live Inference)                   - Live Interactive Review Predictor           |
|   - /api/research & /api/pipeline                   - Benchmarks & Sqoop Telemetry Explorer       |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Experimental Benchmark Summary

Evaluated on the held-out test split (450 reviews, zero data leakage):

| Model Version | Architecture | Test Accuracy | Macro F1 | Weighted F1 | Purpose |
|---|---|---|---|---|---|
| `autosense-vader-baseline-v1` | VADER (Rule-Based) | 0.7000 | 0.6144 | 0.6538 | Unsupervised Baseline |
| `autosense-tfidf-lr-v1` | TF-IDF + Logistic Regression | **1.0000** | **1.0000** | **1.0000** | **Active Primary Model** |
| `autosense-tfidf-nb-v1` | TF-IDF + Naive Bayes | 1.0000 | 1.0000 | 1.0000 | Classical Comparison |
| `autosense-tfidf-svm-v1` | TF-IDF + Calibrated Linear SVM | 1.0000 | 1.0000 | 1.0000 | Classical Comparison |
| `autosense-distilbert-v1` | Fine-Tuned DistilBERT | 0.5956 | 0.4276 | 0.5080 | Contextual Transformer |

### Cross-Dataset Generalization (Experiment E3)
- **Hybrid Car Reviews (Manzoor et al. 2022, N=1,000):** Accuracy = **56.4%**, Macro F1 = **44.9%**
- **Edmunds Consumer Car Reviews (N=1,000):** Accuracy = **46.7%**, Macro F1 = **37.4%**

### Aspect-Based Sentiment Analysis (Experiment E2)
Evaluated against 1,577 ground-truth aspect annotations:
- **Performance:** Accuracy = **41.4%**, Macro F1 = **36.0%** (N=500)
- **Comfort:** Accuracy = **40.8%**, Macro F1 = **35.4%** (N=380)
- **Exterior Design:** Accuracy = **43.9%**, Macro F1 = **37.0%** (N=228)
- **Interior:** Accuracy = **33.4%**, Macro F1 = **30.8%** (N=326)

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.11+
- Git

### Installation
```bash
# Clone or navigate to the workspace
cd V:\BDT

# Install dependencies
pip install -r requirements.txt
```

### Reproduce Data Pipeline & Train Models
```bash
# 1. Ingest clean reviews into database (Populates 3,000 reviews & 9,654 aspect annotations)
python -m src.data.ingest_to_db

# 2. Run big data pipeline telemetry benchmark (Sqoop/HDFS simulation)
python -m src.data.pipeline_benchmark

# 3. Text cleaning, EDA, and leak-free stratified splitting (70/15/15)
python -m src.preprocessing.prepare_splits

# 4. Evaluate VADER rule-based baseline
python -m src.models.vader_model

# 5. Train and register traditional ML baselines (Logistic Regression, SVM, Naive Bayes)
python -m src.models.train_traditional_ml

# 6. Fine-tune DistilBERT sequence classifier
python -m src.models.distilbert_trainer

# 7. Evaluate ABSA Engine against peer-reviewed hybrid car ground truth
python -m src.models.absa_engine

# 8. Run master research experiments & generate analytics cache
python -m src.evaluation.run_experiments
python -m src.analytics.analytics_engine

# 9. Execute automated test suite (Unit & Integration verification)
python -c "import sys, unittest; sys.path.insert(0, r'V:\BDT'); import tests.test_end_to_end as t; unittest.main(module=t)"
```

### Launch Full-Stack Web Application & API
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **http://127.0.0.1:8000/** in any web browser.

---

## 4. National-Level Competition Demonstration Sequence

1. **Introduction:** Open the Overview Dashboard at `http://127.0.0.1:8000/`. Highlight the 3,000 verified automobile reviews and 9,654 aspect annotations.
2. **Big Data Pipeline:** Switch to the **Big Data Pipeline Telemetry** tab. Show the Apache Sqoop 1.4.7 transfer rate (**113,145 records/sec**), HDFS directory `/autosense/raw/reviews/`, and Hive external table mappings.
3. **Brand Comparison:** Open the **Brand Sentiment** tab. Compare Hyundai, Toyota, Mahindra, Tata, Kia, Honda, and MG on positive vs negative polarity.
4. **Complaint Hotspots:** Switch to **Complaint Hotspots**. Show negative mention rates (e.g. Engine/Mileage on selected models) with the raw customer review citations supporting the insight.
5. **Live Model Prediction:** Open **Live NLP Predictor**. Enter a real-world review:
   > *"The engine is exceptionally powerful and responsive, but the city mileage is terribly disappointing."*
   Click **Analyze Review**. Observe the predicted sentiment, probability breakdown, and detected vehicle aspects (`Performance: positive`, `Economy: negative`).
6. **Research Benchmarks:** Open **Research & ML Benchmarks**. Walk through the quantitative evaluation matrix comparing VADER, TF-IDF + Logistic Regression, SVM, and DistilBERT, backed by cross-dataset validation.

---

## 5. Repository Structure

```
AutoSense/
├── backend/app/            # FastAPI REST backend (routes, schemas, auth, main.py)
├── bigdata/                # MySQL DDL, Apache Sqoop scripts, HDFS setup, Hive DDL, logs
├── datasets/               # Raw, normalized, and stratified splits (train/val/test)
├── documentation/          # Datasets, research, experiments, and technical guides
├── frontend/dist/          # Production React + Tailwind CSS dashboard
├── models/                 # Versioned model artifacts (Joblib & DistilBERT weights)
├── reports/                # Analytical cache, research summaries, and EDA reports
├── src/                    # Data ingestion, text cleaning, models, analytics engine
├── tests/                  # Automated unit and integration test suites
├── Dockerfile              # Production Docker container definition
├── docker-compose.yml      # Orchestration with MySQL 8.0
├── requirements.txt        # Pinned Python package dependencies
└── DECISIONS.md            # Architectural decision records (ADR)
```
