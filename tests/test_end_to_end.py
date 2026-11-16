"""
AutoSense Comprehensive End-to-End Integration & System Test Suite (Phase 13)
Verifies:
1. Relational Database & Ingestion Integrity (12,000 reviews, 18,000+ aspect observations)
2. 15 Automobile Brands & 8-Aspect Locked Taxonomy
3. Text Preprocessing & Negation Preservation
4. Data Splitting & Leakage Prevention (Zero Overlap)
5. VADER Rule-Based Baseline Prediction
6. Classical ML Pipelines (TF-IDF + LR / SVM achieving >=88% accuracy)
7. Aspect-Based Sentiment Analysis (ABSA) Engine
8. Prediction Explainability (Feature Attribution)
9. Batch Prediction & Auto-Grouping by Brand/Model
10. AutoSense AI Copilot Chatbot Engine
11. FastAPI Route Handlers & Data Contracts
"""
import unittest
import os
import json
import pandas as pd
from src.data.database import get_session, Review, ReviewAspect
from src.preprocessing.text_cleaner import clean_automobile_text
from src.preprocessing.taxonomy import AUTOMOTIVE_TAXONOMY, get_taxonomy_summary
from src.models.vader_model import VaderBaseline
from src.prediction.predict import AutoSensePredictor
from src.models.absa_engine import AutoSenseABSAEngine
from src.analytics.chatbot import AutoSenseChatbot
from backend.app.routes.api import (
    get_dashboard_summary, get_brands, get_aspects, get_complaints,
    predict_sentiment, predict_batch, chat_with_copilot, get_taxonomy,
    PredictRequest, BatchPredictRequest, ChatRequest, search_reviews
)

class TestAutoSenseEndToEnd(unittest.TestCase):

    def setUp(self):
        self.sample_review_positive = "The engine is silky smooth, powerful and delivers remarkable 22kmpl mileage on highways!"
        self.sample_review_negative = "The cabin is not comfortable, air conditioning failed, and dealership service is terribly rude."
        self.sample_review_mixed = "The exterior design looks stunning, but the braking stability is disappointing."

    def test_01_database_records_and_aspect_links(self):
        session = get_session()
        review_count = session.query(Review).count()
        aspect_count = session.query(ReviewAspect).count()
        session.close()
        
        self.assertGreaterEqual(review_count, 12000, "Database should contain at least 12,000 reviews")
        self.assertGreaterEqual(aspect_count, 18000, "Expected at least 18,000 normalized aspect observations")

    def test_02_fifteen_brands_and_eight_aspects(self):
        # 15 brands check
        session = get_session()
        brands = [r[0] for r in session.query(Review.brand).distinct().all()]
        session.close()
        self.assertGreaterEqual(len(brands), 15, "Corpus must cover at least 15 brands")
        
        # 8-aspect taxonomy check
        tax = get_taxonomy_summary()
        self.assertEqual(len(tax), 8, "Taxonomy must lock exactly 8 core aspect categories")
        expected_cats = {"Performance", "Economy", "Comfort", "Technology", "Safety", "Design", "Ownership", "Value"}
        actual_cats = set(AUTOMOTIVE_TAXONOMY.keys())
        self.assertEqual(actual_cats, expected_cats)

    def test_03_text_cleaner_negation_and_specs(self):
        text = "Car didn't have 1.5L turbo lag! Fuel was <18kmpl> & not noisy at all... https://edmunds.com"
        cleaned = clean_automobile_text(text)
        self.assertIn("did not", cleaned)
        self.assertIn("not noisy", cleaned)
        self.assertIn("1.5", cleaned)
        self.assertNotIn("https", cleaned)
        self.assertNotIn("<", cleaned)

    def test_04_zero_data_leakage_in_splits(self):
        train = pd.read_csv("Datasets/splits/train/train.csv")
        val = pd.read_csv("Datasets/splits/validation/val.csv")
        test = pd.read_csv("Datasets/splits/test/test.csv")
        
        train_ids = set(train['review_id'])
        val_ids = set(val['review_id'])
        test_ids = set(test['review_id'])
        
        self.assertEqual(len(train_ids.intersection(val_ids)), 0, "Leakage between train and val")
        self.assertEqual(len(train_ids.intersection(test_ids)), 0, "Leakage between train and test")
        self.assertEqual(len(val_ids.intersection(test_ids)), 0, "Leakage between val and test")

    def test_05_vader_baseline(self):
        vader = VaderBaseline()
        pos_res = vader.predict_single(self.sample_review_positive)
        neg_res = vader.predict_single(self.sample_review_negative)
        self.assertEqual(pos_res["sentiment"], "positive")
        self.assertEqual(neg_res["sentiment"], "negative")

    def test_06_classical_ml_high_accuracy_target(self):
        registry_path = "models/model_registry/model_registry.json"
        self.assertTrue(os.path.exists(registry_path), "Model registry file missing")
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            
        lr_acc = registry["autosense-tfidf-lr-v1"]["test_accuracy"]
        svm_acc = registry["autosense-tfidf-svm-v1"]["test_accuracy"]
        
        self.assertGreaterEqual(lr_acc, 0.88, "Logistic Regression test accuracy should be >= 88%")
        self.assertGreaterEqual(svm_acc, 0.88, "Linear SVM test accuracy should be >= 88%")

    def test_07_prediction_explainability(self):
        predictor = AutoSensePredictor("autosense-tfidf-lr-v1")
        res = predictor.predict_review(self.sample_review_positive)
        self.assertEqual(res["predicted_sentiment"], "positive")
        self.assertIn("confidence_percentage", res)
        self.assertGreaterEqual(res["confidence_percentage"], 50.0)
        self.assertIn("explainability", res)
        self.assertIn("top_features", res["explainability"])
        self.assertGreater(len(res["explainability"]["top_features"]), 0)

    def test_08_batch_prediction_and_grouping(self):
        predictor = AutoSensePredictor("autosense-tfidf-lr-v1")
        batch_input = [
            {"review_id": 1, "brand": "Mahindra", "vehicle_model": "Thar", "review_text": "Massive engine torque and off-road grip."},
            {"review_id": 2, "brand": "Tata Motors", "vehicle_model": "Harrier", "review_text": "Great road presence but noisy infotainment."}
        ]
        res = predictor.predict_batch(batch_input)
        self.assertEqual(res["total_processed"], 2)
        self.assertIn("brand_summary", res)
        self.assertIn("Mahindra", res["brand_summary"])
        self.assertIn("Tata Motors", res["brand_summary"])

    def test_09_domain_chatbot_copilot(self):
        bot = AutoSenseChatbot()
        ans = bot.ask("Which brand has the highest customer rating?")
        self.assertIn("Nissan", ans["response"])
        self.assertEqual(ans["intent"], "brand_ranking")

    def test_10_fastapi_route_contracts(self):
        dash = get_dashboard_summary()
        self.assertIn("kpi", dash)
        self.assertGreaterEqual(dash["kpi"]["total_reviews"], 12000)
        
        brands = get_brands()
        self.assertGreaterEqual(len(brands), 15)
        
        complaints = get_complaints()
        self.assertGreaterEqual(len(complaints), 5)
        
        pred_res = predict_sentiment(PredictRequest(review_text="Superb pickup and very reliable engine."))
        self.assertEqual(pred_res.predicted_sentiment, "positive")
        self.assertGreater(len(pred_res.aspects_detected), 0)

if __name__ == '__main__':
    unittest.main()
