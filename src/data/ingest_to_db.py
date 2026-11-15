"""
AutoSense Data Ingestion Module
Ingests inspected clean datasets into relational storage (MySQL / SQLite)
Populates 'dataset_sources', 'reviews', and 'review_aspects'.
"""
import os
import pandas as pd
from datetime import datetime
from src.data.database import get_session, DatasetSource, Review, ReviewAspect

def ingest_all():
    session = get_session()
    print("Starting AutoSense Data Ingestion...")
    
    # Register Sources
    sources_data = [
        DatasetSource(
            source_id="SRC_AUTO_1000",
            source_name="automobile_sentiment_1000_reviews.xlsx",
            total_records=1000,
            license_notes="Primary benchmark with 8 brands, timestamps, and 5 aspect categories",
            ingestion_status="ACTIVE"
        ),
        DatasetSource(
            source_id="SRC_AUTO_2000",
            source_name="automobile_sentiment_2000_same_format.xlsx",
            total_records=2000,
            license_notes="Primary benchmark with 8 brands, timestamps, and 5 aspect categories",
            ingestion_status="ACTIVE"
        )
    ]
    
    for s in sources_data:
        existing = session.query(DatasetSource).filter_by(source_id=s.source_id).first()
        if not existing:
            session.add(s)
    session.commit()
    print("Registered dataset sources in database.")
    
    # Ingest automobile_sentiment_1000_reviews
    fp1 = r"V:\BDT\Datasets\automobile_sentiment_1000_reviews.xlsx"
    df1 = pd.read_excel(fp1)
    
    # Ingest automobile_sentiment_2000_same_format
    fp2 = r"V:\BDT\Datasets\automobile_sentiment_2000_same_format.xlsx"
    df2 = pd.read_excel(fp2)
    
    combined_files = [("SRC_AUTO_1000", "automobile_sentiment_1000_reviews", df1),
                      ("SRC_AUTO_2000", "automobile_sentiment_2000_same_format", df2)]
    
    total_reviews_inserted = 0
    total_aspects_inserted = 0
    
    aspect_col_map = {
        'aspect_engine': 'Performance',
        'aspect_safety': 'Safety',
        'aspect_comfort': 'Comfort',
        'aspect_exterior': 'Design',
        'aspect_service': 'Service & Ownership'
    }
    
    for source_id, source_name, df in combined_files:
        print(f"Ingesting {source_name} ({len(df)} rows)...")
        for _, row in df.iterrows():
            rev_id = int(row['review_id'])
            # Check duplicate
            if session.query(Review).filter_by(review_id=rev_id).first():
                continue
                
            rev_date = None
            if pd.notna(row.get('review_timestamp')):
                try:
                    rev_date = pd.to_datetime(row['review_timestamp']).to_pydatetime()
                except Exception:
                    rev_date = None
                    
            sentiment_raw = str(row.get('sentiment', 'neutral')).strip().lower()
            if sentiment_raw not in ['positive', 'negative', 'neutral']:
                sentiment_raw = 'neutral'
                
            rev = Review(
                review_id=rev_id,
                source_id=source_id,
                source_name=source_name,
                brand=str(row.get('brand', 'Unknown')),
                vehicle_model=str(row.get('vehicle_model', 'Unknown')),
                review_text_original=str(row.get('review_text', '')),
                review_text_processed=str(row.get('review_text', '')).strip(),
                language=str(row.get('language', 'en')),
                review_date=rev_date,
                overall_rating=float(row['rating']) if pd.notna(row.get('rating')) else None,
                original_sentiment_label=str(row.get('sentiment', 'neutral')),
                normalized_sentiment_label=sentiment_raw
            )
            session.add(rev)
            total_reviews_inserted += 1
            
            # Aspect rows
            for col, cat_name in aspect_col_map.items():
                if col in row and pd.notna(row[col]):
                    val = str(row[col]).strip().lower()
                    if val in ['positive', 'negative', 'neutral']:
                        asp = ReviewAspect(
                            review_id=rev_id,
                            aspect_category=cat_name,
                            aspect_term=cat_name.lower(),
                            opinion_term=val,
                            aspect_sentiment=val
                        )
                        session.add(asp)
                        total_aspects_inserted += 1
                        
        session.commit()
        
    print(f"Ingestion Complete! Ingested {total_reviews_inserted} reviews and {total_aspects_inserted} aspect observations.")
    session.close()

if __name__ == '__main__':
    ingest_all()
