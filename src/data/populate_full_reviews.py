"""
AutoSense - Populate Full 12,000 Reviews and Aspect Observations
Populates the 'reviews' and 'review_aspects' tables in SQLite with the unified 12,000 corpus
using the locked 8 automotive aspect categories.
"""
import os
import pandas as pd
from datetime import datetime
from src.data.database import get_session, Review, ReviewAspect
from src.preprocessing.text_cleaner import clean_automobile_text
from src.models.absa_engine import AutoSenseABSAEngine

def populate_database():
    print("=" * 70)
    print("AutoSense: Populating Full 12,000 Reviews Database with 8 Aspects")
    print("=" * 70)
    
    session = get_session()
    
    # Check if already populated
    existing_count = session.query(Review).count()
    if existing_count >= 12000:
        print(f"Database already contains {existing_count} reviews. Skipping full reload.")
        session.close()
        return
        
    print("Clearing existing reviews for clean full corpus update...")
    session.query(ReviewAspect).delete()
    session.query(Review).delete()
    session.commit()
    
    df = pd.read_csv("Datasets/normalized/automobile_reviews_unified_12000.csv")
    print(f"Processing {len(df)} reviews...")
    
    absa = AutoSenseABSAEngine()
    
    review_objs = []
    aspect_objs = []
    
    for idx, row in df.iterrows():
        raw_text = str(row['review_text']) if pd.notna(row['review_text']) else ""
        cleaned = clean_automobile_text(raw_text)
        sentiment = str(row['sentiment']).lower()
        if sentiment not in ['positive', 'negative', 'neutral']:
            sentiment = 'neutral'
            
        try:
            rating = float(row['rating']) if pd.notna(row['rating']) else 3.0
        except:
            rating = 3.0
            
        # Parse timestamp
        ts_str = str(row.get('review_timestamp', '2023-01-01'))
        try:
            review_date = datetime.strptime(ts_str[:10], "%Y-%m-%d")
        except:
            review_date = datetime(2023, 1, 1)
            
        rev_id = int(row['review_id'])
        source_name = str(row.get('source', 'CarWale'))
        r_obj = Review(
            review_id=rev_id,
            source_id="SRC_001",
            source_name=source_name,
            brand=str(row.get('brand', 'Unknown')),
            vehicle_model=str(row.get('vehicle_model', 'Unknown')),
            review_text_original=raw_text,
            review_text_processed=cleaned,
            overall_rating=rating,
            original_sentiment_label=sentiment,
            normalized_sentiment_label=sentiment,
            review_date=review_date
        )
        review_objs.append(r_obj)
        
        # Aspect extraction on the review
        aspects = absa.extract_aspect_sentiments(raw_text)
        for asp in aspects:
            asp_obj = ReviewAspect(
                review_id=rev_id,
                aspect_category=asp['aspect_category'],
                aspect_term=asp['matched_keyword'],
                opinion_term=asp['aspect_sentiment'],
                aspect_sentiment=asp['aspect_sentiment']
            )
            aspect_objs.append(asp_obj)
            
        if len(review_objs) >= 1000:
            session.bulk_save_objects(review_objs)
            session.bulk_save_objects(aspect_objs)
            session.commit()
            print(f"  Committed batch up to review {rev_id} ({len(aspect_objs)} aspect observations)...")
            review_objs = []
            aspect_objs = []
            
    if review_objs:
        session.bulk_save_objects(review_objs)
        session.bulk_save_objects(aspect_objs)
        session.commit()
        
    total_revs = session.query(Review).count()
    total_asps = session.query(ReviewAspect).count()
    print(f"\nSuccessfully populated database: {total_revs} reviews, {total_asps} aspect observations.")
    session.close()

if __name__ == "__main__":
    populate_database()
