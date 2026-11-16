# AutoSense Exploratory Data Analysis (EDA) & Splitting Report

- **Total Reviews:** 15000
- **Sentiment Class Breakdown:**
  - `positive`: 9362 (62.41%)
  - `neutral`: 3381 (22.54%)
  - `negative`: 2257 (15.05%)

## Text Characteristics
- Average Word Count: 44.31 words
- Average Character Length: 242.17 characters
- Range: 0 to 8303 characters

## Data Splitting Strategy
- **Methodology:** Stratified random split with seed 42 to preserve exact class priors without data leakage.
- **Training Set (70%):** 10500 reviews (Positive: 6553, Neutral: 2367, Negative: 1580)
- **Validation Set (15%):** 2250 reviews
- **Held-Out Test Set (15%):** 2250 reviews (Reserved strictly for final evaluation)
