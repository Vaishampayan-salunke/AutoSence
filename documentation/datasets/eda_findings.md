# AutoSense Exploratory Data Analysis (EDA) & Splitting Report

- **Total Reviews:** 3000
- **Sentiment Class Breakdown:**
  - `positive`: 1548 (51.6%)
  - `neutral`: 800 (26.67%)
  - `negative`: 652 (21.73%)

## Text Characteristics
- Average Word Count: 14.45 words
- Average Character Length: 88.61 characters
- Range: 58 to 126 characters

## Data Splitting Strategy
- **Methodology:** Stratified random split with seed 42 to preserve exact class priors without data leakage.
- **Training Set (70%):** 2100 reviews (Positive: 1084, Neutral: 560, Negative: 456)
- **Validation Set (15%):** 450 reviews
- **Held-Out Test Set (15%):** 450 reviews (Reserved strictly for final evaluation)
