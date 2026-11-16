"""
AutoSense Unit & Integration Test Suite
Validates text preprocessing, database models, model loading, and live predictions.
"""
import unittest
import os
from pathlib import Path
import pandas as pd
from src.preprocessing.text_cleaner import clean_automobile_text
from src.data.database import get_session, Review, DatasetSource
from src.models.vader_model import VaderBaseline
from src.prediction.predict import AutoSensePredictor

class TestAutoSensePipeline(unittest.TestCase):
    
    def test_text_cleaner(self):
        sample = "The car didn't perform well! Mileage was <15kmpl> & it's noisy... https://carwale.com"
        cleaned = clean_automobile_text(sample)
        # Verify negation preserved
        self.assertIn("did not", cleaned)
        # Verify URL removed
        self.assertNotIn("https", cleaned)
        # Verify HTML stripped
        self.assertNotIn("<", cleaned)
        
    def test_database_records(self):
        session = get_session()
        review_count = session.query(Review).count()
        sources_count = session.query(DatasetSource).count()
        session.close()
        self.assertGreaterEqual(review_count, 3000, "Expected at least 3000 reviews in database")
        self.assertGreaterEqual(sources_count, 2, "Expected at least 2 registered sources")
        
    def test_vader_baseline(self):
        vader = VaderBaseline()
        res_pos = vader.predict_single("Outstanding performance and wonderful mileage!")
        self.assertEqual(res_pos["sentiment"], "positive")
        res_neg = vader.predict_single("Terrible engine noise and pathetic customer service.")
        self.assertEqual(res_neg["sentiment"], "negative")
        
    def test_predictor_model(self):
        predictor = AutoSensePredictor("autosense-tfidf-lr-v1")
        res = predictor.predict_review("The car is exceptionally smooth, reliable and fuel efficient.")
        self.assertEqual(res["predicted_sentiment"], "positive")
        self.assertIn("probabilities", res)
        self.assertIn("aspects_detected", res)
        
    def test_splits_integrity(self):
        project_root = Path(__file__).resolve().parents[1]
        train_path = project_root / "Datasets" / "splits" / "train" / "train.csv"
        test_path = project_root / "Datasets" / "splits" / "test" / "test.csv"
        self.assertTrue(os.path.exists(train_path))
        self.assertTrue(os.path.exists(test_path))
        
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        # Check no overlap between train and test review_ids (leakage check)
        train_ids = set(train_df['review_id'])
        test_ids = set(test_df['review_id'])
        overlap = train_ids.intersection(test_ids)
        self.assertEqual(len(overlap), 0, "Data leakage detected: train and test sets have overlapping review_ids!")

if __name__ == '__main__':
    unittest.main()
