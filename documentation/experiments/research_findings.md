# AutoSense Research Experiments & Empirical Evaluation

## Experiment E1: Sentiment Model Comparison (Held-Out Test Set)

| Model Version | Architecture | Accuracy | Macro F1 | Weighted F1 |
|---|---|---|---|---|
| `autosense-vader-baseline-v1` | VADER (Rule-Based Baseline) | 0.7000 | 0.6144 | 0.6538 |
| `autosense-tfidf-lr-v1` | TF-IDF + Logistic Regression (Main Baseline) | 1.0000 | 1.0000 | 1.0000 |
| `autosense-tfidf-nb-v1` | TF-IDF + Multinomial Naive Bayes | 1.0000 | 1.0000 | 1.0000 |
| `autosense-tfidf-svm-v1` | TF-IDF + Linear SVM (Calibrated) | 1.0000 | 1.0000 | 1.0000 |
| `autosense-distilbert-v1` | autosense-distilbert-v1 | 0.5956 | 0.4276 | 0.5080 |

## Experiment E3: Cross-Dataset Generalization

| Benchmark Dataset | Sample Size | Accuracy | Macro F1 |
|---|---|---|---|
| Hybrid Car Online Reviews (Manzoor et al., 2022) | 1000 | 0.5640 | 0.4485 |
| Edmunds Consumer Car Reviews | 1000 | 0.4670 | 0.3738 |

## Experiment E4: Apache Sqoop & Big Data Pipeline Performance

- **Total Records Ingested:** 12654
- **Overall Pipeline Throughput:** 62794.0 records/sec
- **Payload Transferred:** 1075.14 KB

## Experiment E5: Automobile Complaint Hotspots (Top 5)

| Brand | Aspect Category | Complaint Rate (%) | Negative Mentions | Total Mentions |
|---|---|---|---|---|
| Maruti Suzuki | Service & Ownership | **26.94%** | 66 | 245 |
| Mahindra | Service & Ownership | **26.46%** | 59 | 223 |
| Mahindra | Safety | **25.74%** | 61 | 237 |
| Mahindra | Performance | **24.81%** | 67 | 270 |
| Honda | Service & Ownership | **24.41%** | 52 | 213 |
