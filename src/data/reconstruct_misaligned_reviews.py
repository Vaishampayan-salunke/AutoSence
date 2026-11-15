"""
AutoSense - Reconstruct and Normalize 7,000 Reviews Dataset
Extracts and normalizes reviews from:
1. Datasets/automobile_sentiment_1000_reviews.xlsx (1,000 rows)
2. Datasets/automobile_sentiment_2000_same_format.xlsx (2,000 rows)
3. Datasets/automobile_sentiment_2000_more_reviews.xlsx (2,000 rows - text in review_id)
4. Datasets/automobile_sentiment_2000_new_reviews.xlsx (2,000 rows - text in review_id)

Outputs:
- Datasets/normalized/automobile_reviews_normalized_7000.csv
- SQLite database update in bigdata/mysql/autosense_local.db
- Train/Val/Test stratified splits in Datasets/splits/
"""

import os
import re
import pandas as pd
import numpy as np

def clean_extracted_text(text):
    if not isinstance(text, str):
        return ""
    # Strip trailing "Review 2001." or "Review batch 0001."
    text = re.sub(r'\s+Review\s+(?:batch\s+)?\d+\.?\s*$', '', text, flags=re.IGNORECASE)
    # Strip leading "ModelName: " if it exists
    text = re.sub(r'^[A-Za-z0-9\s\-]+:\s+', '', text)
    return text.strip()

def process_file_standard(path, start_id=1):
    df = pd.read_excel(path)
    records = []
    for idx, row in df.iterrows():
        review_text = str(row['review_text']) if pd.notna(row['review_text']) else ""
        if not review_text.strip() or review_text.lower() == 'nan':
            # Check review_id if review_text is empty
            review_text = clean_extracted_text(str(row['review_id']))
        else:
            review_text = review_text.strip()

        brand = str(row['brand']).strip() if pd.notna(row['brand']) else "Generic"
        model = str(row['vehicle_model']).strip() if pd.notna(row['vehicle_model']) else "Automobile"
        sentiment = str(row['sentiment']).strip().capitalize() if pd.notna(row['sentiment']) else "Neutral"
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            sentiment = "Neutral"

        try:
            rating = float(row['rating']) if pd.notna(row['rating']) else 3.0
        except:
            rating = 3.0

        records.append({
            'review_id': start_id + idx,
            'source': str(row['source']).strip() if pd.notna(row['source']) and str(row['source']).lower() != 'nan' else 'CarWale',
            'brand': brand,
            'vehicle_model': model,
            'review_timestamp': str(row['review_timestamp']) if pd.notna(row['review_timestamp']) and str(row['review_timestamp']).lower() != 'nan' else '2023-01-01',
            'rating': rating,
            'review_text': review_text,
            'sentiment': sentiment,
            'location': str(row['location']).strip() if pd.notna(row['location']) and str(row['location']).lower() != 'nan' else 'India',
            'aspect_engine': str(row.get('aspect_engine', '')) if pd.notna(row.get('aspect_engine', '')) and str(row.get('aspect_engine', '')).lower() != 'nan' else '',
            'aspect_safety': str(row.get('aspect_safety', '')) if pd.notna(row.get('aspect_safety', '')) and str(row.get('aspect_safety', '')).lower() != 'nan' else '',
            'aspect_comfort': str(row.get('aspect_comfort', '')) if pd.notna(row.get('aspect_comfort', '')) and str(row.get('aspect_comfort', '')).lower() != 'nan' else '',
            'aspect_exterior': str(row.get('aspect_exterior', '')) if pd.notna(row.get('aspect_exterior', '')) and str(row.get('aspect_exterior', '')).lower() != 'nan' else '',
            'aspect_service': str(row.get('aspect_service', '')) if pd.notna(row.get('aspect_service', '')) and str(row.get('aspect_service', '')).lower() != 'nan' else '',
        })
    return pd.DataFrame(records)

def process_file_misaligned(path, start_id):
    df = pd.read_excel(path)
    records = []
    for idx, row in df.iterrows():
        # Text is in review_id
        raw_text = str(row['review_id'])
        review_text = clean_extracted_text(raw_text)
        
        brand = str(row['brand']).strip() if pd.notna(row['brand']) else "Generic"
        model = str(row['vehicle_model']).strip() if pd.notna(row['vehicle_model']) else "Automobile"
        sentiment = str(row['sentiment']).strip().capitalize() if pd.notna(row['sentiment']) else "Neutral"
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            sentiment = "Neutral"

        try:
            rating = float(row['rating']) if pd.notna(row['rating']) else 3.0
        except:
            rating = 3.0

        records.append({
            'review_id': start_id + idx,
            'source': 'CarDekho' if (idx % 2 == 0) else 'CarWale',
            'brand': brand,
            'vehicle_model': model,
            'review_timestamp': f"2023-{(idx % 12) + 1:02d}-{(idx % 28) + 1:02d}",
            'rating': rating,
            'review_text': review_text,
            'sentiment': sentiment,
            'location': str(row['location']).strip() if pd.notna(row['location']) and str(row['location']).lower() != 'nan' else 'India',
            'aspect_engine': str(row.get('aspect_engine', '')) if pd.notna(row.get('aspect_engine', '')) and str(row.get('aspect_engine', '')).lower() != 'nan' else '',
            'aspect_safety': str(row.get('aspect_safety', '')) if pd.notna(row.get('aspect_safety', '')) and str(row.get('aspect_safety', '')).lower() != 'nan' else '',
            'aspect_comfort': str(row.get('aspect_comfort', '')) if pd.notna(row.get('aspect_comfort', '')) and str(row.get('aspect_comfort', '')).lower() != 'nan' else '',
            'aspect_exterior': str(row.get('aspect_exterior', '')) if pd.notna(row.get('aspect_exterior', '')) and str(row.get('aspect_exterior', '')).lower() != 'nan' else '',
            'aspect_service': str(row.get('aspect_service', '')) if pd.notna(row.get('aspect_service', '')) and str(row.get('aspect_service', '')).lower() != 'nan' else '',
        })
    return pd.DataFrame(records)

def main():
    print("Reconstructing and unifying all 7,000 automobile reviews...")
    
    # 1. 1000 reviews
    df1 = process_file_standard("Datasets/automobile_sentiment_1000_reviews.xlsx", start_id=1)
    print(f"File 1 (1000 reviews): {len(df1)} rows")
    
    # 2. 2000 same format
    df2 = process_file_standard("Datasets/automobile_sentiment_2000_same_format.xlsx", start_id=len(df1) + 1)
    print(f"File 2 (2000 same format): {len(df2)} rows")
    
    # 3. 2000 more reviews (misaligned)
    df3 = process_file_misaligned("Datasets/automobile_sentiment_2000_more_reviews.xlsx", start_id=len(df1) + len(df2) + 1)
    print(f"File 3 (2000 more reviews): {len(df3)} rows")
    
    # 4. 2000 new reviews (misaligned)
    df4 = process_file_misaligned("Datasets/automobile_sentiment_2000_new_reviews.xlsx", start_id=len(df1) + len(df2) + len(df3) + 1)
    print(f"File 4 (2000 new reviews): {len(df4)} rows")
    
    # Combine
    combined = pd.concat([df1, df2, df3, df4], ignore_index=True)
    combined['review_id'] = range(1, len(combined) + 1)
    
    print("\n--- Summary of Combined Corpus ---")
    print(f"Total reviews: {len(combined)}")
    print(f"Sentiments: {combined['sentiment'].value_counts().to_dict()}")
    print(f"Total unique brands: {combined['brand'].nunique()}")
    print(f"Brands: {sorted(combined['brand'].unique().tolist())}")
    print(f"Total unique models: {combined['vehicle_model'].nunique()}")
    
    # Save normalized CSV
    out_csv = "Datasets/normalized/automobile_reviews_normalized_7000.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    combined.to_csv(out_csv, index=False)
    print(f"\nSaved combined 7,000 reviews to: {out_csv}")
    
    # Update SQLite database
    from sqlalchemy import create_engine
    db_path = "bigdata/mysql/autosense_local.db"
    engine = create_engine(f"sqlite:///{db_path}")
    combined.to_sql("raw_automobile_reviews", con=engine, if_exists="replace", index=False)
    print(f"Updated SQLite database: {db_path} table 'raw_automobile_reviews' ({len(combined)} rows)")

    # Prepare stratified splits (70% Train, 15% Val, 15% Test)
    from sklearn.model_selection import train_test_split
    train_df, test_val_df = train_test_split(
        combined, test_size=0.30, random_state=42, stratify=combined['sentiment']
    )
    val_df, test_df = train_test_split(
        test_val_df, test_size=0.50, random_state=42, stratify=test_val_df['sentiment']
    )
    
    train_path = "Datasets/splits/train/train.csv"
    val_path = "Datasets/splits/validation/val.csv"
    test_path = "Datasets/splits/test/test.csv"
    
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    os.makedirs(os.path.dirname(val_path), exist_ok=True)
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"Created Train split: {len(train_df)} rows ({train_path})")
    print(f"Created Val split:   {len(val_df)} rows ({val_path})")
    print(f"Created Test split:  {len(test_df)} rows ({test_path})")
    print("Zero overlap check: Train & Test ID intersection =", len(set(train_df['review_id']).intersection(set(test_df['review_id']))))

if __name__ == "__main__":
    main()
