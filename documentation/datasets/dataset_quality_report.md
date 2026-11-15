# AutoSense Dataset Quality & Audit Report

## 1. Executive Summary

This report establishes the data governance, audit trails, and inclusion/exclusion decisions for datasets collected and prepared for the AutoSense platform.

| Dataset Name | Records | Classification | Usability Verdict | Key Issue / Action |
|---|---|---|---|---|
| `automobile_sentiment_1000_reviews.xlsx` | 1,000 | Primary | **ACCEPTED** | Clean, complete multi-brand reviews with ground-truth sentiment & 5 aspect labels. |
| `automobile_sentiment_2000_same_format.xlsx` | 2,000 | Primary | **ACCEPTED** | Clean, identical schema, valid dates, multi-brand and aspect ratings. |
| `1000 reviews RS_P-7.xlsx` | 1,002 | Primary / Aspect Eval | **ACCEPTED** | Peer-reviewed dataset (Manzoor et al., Data in Brief 2022). Aspect sentence segregated. |
| `MuSe-CarASTE (2025)` | 16,490 (train+dev) | Primary ABSA Benchmark | **ACCEPTED** | Usmani et al. (Expert Systems with Applications 2025). Full ASTE triplet benchmarks. |
| `edmunds_car_reviews.csv` | 13,790 | Supplementary / Eval | **ACCEPTED** | Large-scale real consumer reviews with rating and vehicle title for external evaluation. |
| `amazon_automotive_reviews_50k.csv` | 50,000 | Supplementary / Cross-Domain | **ACCEPTED** | High-volume automotive product reviews with ratings, helpfulness votes, and timestamps. |
| `automobile_sentiment_2000_more_reviews.xlsx` | 2,000 | Excluded | **REJECTED** | Column misalignment: review text shifted into `review_id` field. |
| `automobile_sentiment_2000_new_reviews.xlsx` | 2,000 | Excluded | **REJECTED** | Column misalignment: review text shifted into `review_id` field. |
| `CarPrice_Assignment` & `Used_Car_Price_Data.csv` | 1,205 | Excluded | **REJECTED** | Numerical vehicle specification and pricing datasets without textual feedback. |

## 2. Label Distribution in Primary Training Corpus (3,000 Balanced Vehicle Reviews)

The primary labeled training corpus combines `automobile_sentiment_1000_reviews` and `automobile_sentiment_2000_same_format`:

- **Total Reviews:** 3,000
- **Positive:** 1,548 (51.6%)
- **Neutral:** 800 (26.7%)
- **Negative:** 652 (21.7%)
- **Missing Values in Review Text:** 0 (100% complete)
- **Brands Represented:** 8 major brands (Hyundai, Toyota, Mahindra, Tata, Maruti Suzuki, Kia, Honda, MG)
- **Review Date Coverage:** 2025-01-01 through 2026-10-31

## 3. Exclusion Justifications (Rigorous Research Compliance)

1. **Shifted/Misaligned Files (`2000_more_reviews`, `2000_new_reviews`):**
   - In both files, `df['review_text'].isnull().sum() == 2000`.
   - The original text was concatenated with vehicle metadata into the ID field (e.g., `"EV6: Mileage has been satisfactory for my regular commute... Review 2001."`).
   - Rather than silently training on corrupted column mappings, AutoSense isolates these files until an automated parser/repair script reconstructs their true schema.

2. **Numerical Pricing Assignment Datasets:**
   - Datasets contain columns like `fueltype`, `horsepower`, `wheelbase`, `Price($)`. They do not contain user-authored sentiment expressions. Excluded from NLP training.
