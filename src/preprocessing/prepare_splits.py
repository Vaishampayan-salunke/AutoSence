"""
AutoSense Data Preparation, EDA & Splitting Module
Generates leak-free, stratified train/validation/test splits and comprehensive EDA reports.
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from src.data.database import get_session, Review
from src.preprocessing.text_cleaner import clean_automobile_text

def prepare_and_split():
    session = get_session()
    print("Loading review corpus from database...")
    reviews = session.query(Review).all()
    
    data = []
    for r in reviews:
        data.append({
            'review_id': r.review_id,
            'source_id': r.source_id,
            'brand': r.brand,
            'vehicle_model': r.vehicle_model,
            'review_text_original': r.review_text_original,
            'review_date': str(r.review_date) if r.review_date else '',
            'overall_rating': r.overall_rating,
            'sentiment': r.normalized_sentiment_label
        })
    session.close()
    
    df = pd.DataFrame(data)
    print(f"Total reviews loaded: {len(df)}")
    
    # Preprocessing
    df['review_text_processed'] = df['review_text_original'].apply(clean_automobile_text)
    df['char_length'] = df['review_text_processed'].str.len()
    df['word_count'] = df['review_text_processed'].str.split().str.len()
    
    # Save normalized dataset
    norm_path = r"V:\BDT\datasets\normalized\automobile_reviews_normalized_3000.csv"
    os.makedirs(os.path.dirname(norm_path), exist_ok=True)
    df.to_csv(norm_path, index=False)
    print(f"Saved normalized corpus to {norm_path}")
    
    # EDA Metrics
    eda = {
        'total_reviews': len(df),
        'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
        'sentiment_percentages': (df['sentiment'].value_counts(normalize=True) * 100).round(2).to_dict(),
        'brand_distribution': df['brand'].value_counts().to_dict(),
        'model_distribution': df['vehicle_model'].value_counts().head(10).to_dict(),
        'text_length_stats': {
            'mean_chars': round(float(df['char_length'].mean()), 2),
            'median_chars': round(float(df['char_length'].median()), 2),
            'min_chars': int(df['char_length'].min()),
            'max_chars': int(df['char_length'].max()),
            'mean_words': round(float(df['word_count'].mean()), 2),
            'median_words': round(float(df['word_count'].median()), 2)
        },
        'ratings_summary': {
            'mean_rating': round(float(df['overall_rating'].mean()), 2) if df['overall_rating'].notna().any() else None,
            'rating_distribution': df['overall_rating'].value_counts().sort_index().to_dict() if df['overall_rating'].notna().any() else {}
        }
    }
    
    # Stratified Split: 70% Train, 15% Validation, 15% Test
    # Step 1: 70% train, 30% temp
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df['sentiment']
    )
    
    # Step 2: Split temp equally into 15% Val and 15% Test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df['sentiment']
    )
    
    # Add split sizes to EDA
    eda['splits'] = {
        'train_count': len(train_df),
        'train_dist': train_df['sentiment'].value_counts().to_dict(),
        'val_count': len(val_df),
        'val_dist': val_df['sentiment'].value_counts().to_dict(),
        'test_count': len(test_df),
        'test_dist': test_df['sentiment'].value_counts().to_dict()
    }
    
    # Save splits
    train_path = r"V:\BDT\datasets\splits\train\train.csv"
    val_path = r"V:\BDT\datasets\splits\validation\val.csv"
    test_path = r"V:\BDT\datasets\splits\test\test.csv"
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"Stratified Splits Saved successfully:")
    print(f"  - Train:      {len(train_df)} rows ({len(train_df)/len(df)*100:.1f}%) -> {train_path}")
    print(f"  - Validation: {len(val_df)} rows ({len(val_df)/len(df)*100:.1f}%) -> {val_path}")
    print(f"  - Test:       {len(test_df)} rows ({len(test_df)/len(df)*100:.1f}%) -> {test_path}")
    
    # Save EDA JSON
    eda_json_path = r"V:\BDT\reports\eda_report.json"
    with open(eda_json_path, 'w', encoding='utf-8') as f:
        json.dump(eda, f, indent=2)
        
    # Write Markdown EDA Report
    eda_md_path = r"V:\BDT\documentation\datasets\eda_findings.md"
    with open(eda_md_path, 'w', encoding='utf-8') as f:
        f.write("# AutoSense Exploratory Data Analysis (EDA) & Splitting Report\n\n")
        f.write(f"- **Total Reviews:** {eda['total_reviews']}\n")
        f.write(f"- **Sentiment Class Breakdown:**\n")
        for cls, cnt in eda['sentiment_distribution'].items():
            pct = eda['sentiment_percentages'][cls]
            f.write(f"  - `{cls}`: {cnt} ({pct}%)\n")
        f.write("\n## Text Characteristics\n")
        f.write(f"- Average Word Count: {eda['text_length_stats']['mean_words']} words\n")
        f.write(f"- Average Character Length: {eda['text_length_stats']['mean_chars']} characters\n")
        f.write(f"- Range: {eda['text_length_stats']['min_chars']} to {eda['text_length_stats']['max_chars']} characters\n\n")
        f.write("## Data Splitting Strategy\n")
        f.write("- **Methodology:** Stratified random split with seed 42 to preserve exact class priors without data leakage.\n")
        f.write(f"- **Training Set (70%):** {eda['splits']['train_count']} reviews (Positive: {eda['splits']['train_dist'].get('positive')}, Neutral: {eda['splits']['train_dist'].get('neutral')}, Negative: {eda['splits']['train_dist'].get('negative')})\n")
        f.write(f"- **Validation Set (15%):** {eda['splits']['val_count']} reviews\n")
        f.write(f"- **Held-Out Test Set (15%):** {eda['splits']['test_count']} reviews (Reserved strictly for final evaluation)\n")
        
    print(f"Saved EDA reports to {eda_json_path} and {eda_md_path}")

if __name__ == '__main__':
    prepare_and_split()
