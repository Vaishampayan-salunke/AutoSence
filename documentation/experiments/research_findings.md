# AutoSense Research Experiments & Empirical Evaluation

## Experiment E1: Sentiment Model Comparison (Held-Out Test Set)

| Model Version | Architecture | Accuracy | Macro F1 | Weighted F1 |
|---|---|---|---|---|
| `autosense-vader-baseline-v1` | VADER (Rule-Based Baseline) | 0.6782 | 0.4986 | 0.6243 |
| `autosense-tfidf-lr-v1` | TF-IDF + Logistic Regression (Main Baseline) | 0.9284 | 0.9065 | 0.9273 |
| `autosense-tfidf-nb-v1` | TF-IDF + Multinomial Naive Bayes | 0.9227 | 0.9021 | 0.9195 |
| `autosense-tfidf-svm-v1` | TF-IDF + Linear SVM (Calibrated) | 0.9298 | 0.9083 | 0.9279 |
| `autosense-distilbert-v1` | autosense-distilbert-v1 | 0.6422 | 0.3089 | 0.5187 |

## Experiment E3: Cross-Dataset Generalization

| Benchmark Dataset | Sample Size | Accuracy | Macro F1 |
|---|---|---|---|
| Hybrid Car Online Reviews (Manzoor et al., 2022) | 1000 | 0.5350 | 0.4223 |
| Edmunds Consumer Car Reviews | 1000 | 0.7970 | 0.6677 |

## Experiment E4: Apache Sqoop & Big Data Pipeline Performance

- **Total Records Ingested:** 42778
- **Overall Pipeline Throughput:** 36440.56 records/sec
- **Payload Transferred:** 6101.56 KB

## Experiment E5: Automobile Complaint Hotspots (Top 5)

| Brand | Aspect Category | Complaint Rate (%) | Negative Mentions | Total Mentions |
|---|---|---|---|---|
| Nissan | Ownership | **28.93%** | 381 | 1317 |
| Maruti Suzuki | Service & Ownership | **26.94%** | 66 | 245 |
| Toyota | Ownership | **26.88%** | 25 | 93 |
| Maruti Suzuki | Ownership | **26.74%** | 23 | 86 |
| Mahindra | Service & Ownership | **26.46%** | 59 | 223 |
