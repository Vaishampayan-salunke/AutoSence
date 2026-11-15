"""
AutoSense Inference & Prediction Engine
Loads versioned model artifacts and executes prediction pipelines with calibrated probabilities,
explainability feature attribution (why the decision was made), and batch prediction capabilities.
"""
import os
import joblib
import json
import pandas as pd
import numpy as np
from src.preprocessing.text_cleaner import clean_automobile_text
from src.preprocessing.taxonomy import AUTOMOTIVE_TAXONOMY
from src.models.vader_model import VaderBaseline

class AutoSensePredictor:
    def __init__(self, model_version: str = "autosense-tfidf-lr-v1"):
        self.model_version = model_version
        self.artifact_path = os.path.join(r"V:\BDT\models\traditional_ml", f"{model_version}.joblib")
        self.pipeline = None
        self.classes = ['negative', 'neutral', 'positive']
        self.vader = VaderBaseline()
        self.taxonomy = AUTOMOTIVE_TAXONOMY
        
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.artifact_path):
            try:
                self.pipeline = joblib.load(self.artifact_path)
                if hasattr(self.pipeline, 'classes_'):
                    self.classes = list(self.pipeline.classes_)
                elif hasattr(self.pipeline.named_steps['clf'], 'classes_'):
                    self.classes = list(self.pipeline.named_steps['clf'].classes_)
                print(f"Loaded AutoSense model '{self.model_version}' from {self.artifact_path}")
            except Exception as e:
                print(f"Warning: Failed to load model {self.model_version}: {e}. Falling back to VADER.")
                self.pipeline = None
        else:
            print(f"Warning: Artifact {self.artifact_path} not found. Falling back to VADER.")
            self.pipeline = None

    def explain_prediction(self, cleaned_text: str, predicted_class: str) -> dict:
        """
        Computes feature attribution explaining WHY the model made its decision.
        Extracts words in the review that contributed most strongly to the predicted sentiment.
        """
        if not self.pipeline or 'tfidf' not in self.pipeline.named_steps or 'clf' not in self.pipeline.named_steps:
            # Fallback keyword extraction using VADER lexicon
            words = cleaned_text.lower().split()
            attributions = []
            for w in set(words):
                s = self.vader.predict_single(w)
                if abs(s['compound']) >= 0.1:
                    attributions.append({
                        "token": w,
                        "weight": round(float(s['compound']), 4),
                        "direction": "positive" if s['compound'] > 0 else "negative"
                    })
            attributions.sort(key=lambda x: abs(x['weight']), reverse=True)
            return {
                "top_features": attributions[:6],
                "explanation_summary": f"Prediction influenced by emotional keywords: {', '.join([a['token'] for a in attributions[:4]])}"
            }

        try:
            tfidf = self.pipeline.named_steps['tfidf']
            clf = self.pipeline.named_steps['clf']
            feature_names = np.array(tfidf.get_feature_names_out())
            
            # Transform single text
            vec = tfidf.transform([cleaned_text])
            nonzero_indices = vec.indices
            
            if len(nonzero_indices) == 0:
                return {"top_features": [], "explanation_summary": "No prominent vocabulary features detected."}
                
            class_idx = list(self.classes).index(predicted_class) if predicted_class in self.classes else 0
            
            # Extract coefficients
            if hasattr(clf, "coef_"):
                coefs = clf.coef_[class_idx]
            else:
                coefs = np.zeros(len(feature_names))
                
            token_scores = []
            for idx in nonzero_indices:
                token = feature_names[idx]
                tf_val = vec[0, idx]
                weight = float(coefs[idx] * tf_val)
                token_scores.append({
                    "token": token,
                    "weight": round(weight, 4),
                    "direction": "supports" if weight > 0 else "opposes"
                })
                
            # Sort by absolute weight
            token_scores.sort(key=lambda x: abs(x['weight']), reverse=True)
            top_supporting = [t for t in token_scores if t['weight'] > 0][:5]
            top_opposing = [t for t in token_scores if t['weight'] < 0][:3]
            
            summary_words = [t['token'] for t in top_supporting]
            explanation = f"Model classified as '{predicted_class.upper()}' primarily due to strong signaling from terms: {', '.join(summary_words)}." if summary_words else "Decision based on balanced context."
            
            return {
                "top_features": token_scores[:8],
                "supporting_features": top_supporting,
                "opposing_features": top_opposing,
                "explanation_summary": explanation
            }
        except Exception as e:
            return {"top_features": [], "explanation_summary": f"Attribution calculated via baseline: {e}"}

    def predict_review(self, raw_text: str) -> dict:
        """
        Takes raw review text and returns overall sentiment, probability distribution,
        feature attribution explainability, and locked 8-aspect sentiment extractions.
        """
        if not isinstance(raw_text, str) or not raw_text.strip():
            return {
                "error": "Input text must be a non-empty string",
                "review": raw_text
            }
            
        cleaned_text = clean_automobile_text(raw_text)
        
        # 1. Overall Sentiment Prediction
        if self.pipeline:
            pred_class = self.pipeline.predict([cleaned_text])[0]
            if hasattr(self.pipeline, "predict_proba"):
                probs = self.pipeline.predict_proba([cleaned_text])[0]
                prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(self.classes, probs)}
                confidence = float(max(probs))
            else:
                prob_dict = {cls: (1.0 if cls == pred_class else 0.0) for cls in self.classes}
                confidence = 1.0
        else:
            # Fallback to VADER
            vader_res = self.vader.predict_single(raw_text)
            pred_class = vader_res["sentiment"]
            prob_dict = vader_res["scores"]
            confidence = abs(vader_res["compound"])
            
        # 2. Explainability
        explanation = self.explain_prediction(cleaned_text, pred_class)
        
        # 3. Aspect-Based Opinion Extraction (Locked 8 Taxonomy Categories)
        detected_aspects = []
        sentences = [s.strip() for s in raw_text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        
        for category, config in self.taxonomy.items():
            kws = config["keywords"]
            cat_mentions = []
            for s in sentences:
                s_lower = s.lower()
                for kw in kws:
                    if kw in s_lower:
                        sent_score = self.vader.predict_single(s)
                        cat_mentions.append({
                            "aspect_category": category,
                            "keyword": kw,
                            "sentence": s,
                            "aspect_sentiment": sent_score["sentiment"],
                            "compound_score": sent_score["compound"]
                        })
                        break
            if cat_mentions:
                sentiments = [m["aspect_sentiment"] for m in cat_mentions]
                pos_c = sentiments.count("positive")
                neg_c = sentiments.count("negative")
                if pos_c > neg_c:
                    polarity = "positive"
                elif neg_c > pos_c:
                    polarity = "negative"
                else:
                    polarity = "neutral"
                    
                detected_aspects.append({
                    "category": category,
                    "sentiment": polarity,
                    "matched_keyword": cat_mentions[0]["keyword"],
                    "evidence": cat_mentions[0]["sentence"],
                    "compound_score": cat_mentions[0]["compound_score"]
                })
                
        return {
            "review_text": raw_text,
            "cleaned_text": cleaned_text,
            "predicted_sentiment": pred_class,
            "confidence_percentage": round(confidence * 100, 2),
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "explainability": explanation,
            "aspects_detected": detected_aspects,
            "model_version": self.model_version
        }

    def predict_batch(self, reviews: list) -> dict:
        """
        Runs batch prediction, auto-groups by brand and vehicle model,
        and aggregates actionable recommendations.
        """
        results = []
        brand_summary = {}
        model_summary = {}
        complaint_hotspots = {}
        
        for item in reviews:
            text = item.get("review_text", "")
            brand = item.get("brand", "Unknown")
            model = item.get("vehicle_model", "Unknown")
            
            res = self.predict_review(text)
            res["brand"] = brand
            res["vehicle_model"] = model
            results.append(res)
            
            # Aggregate brand stats
            if brand not in brand_summary:
                brand_summary[brand] = {"total": 0, "positive": 0, "neutral": 0, "negative": 0}
            brand_summary[brand]["total"] += 1
            brand_summary[brand][res["predicted_sentiment"]] += 1
            
            # Aggregate model stats
            if model not in model_summary:
                model_summary[model] = {"brand": brand, "total": 0, "positive": 0, "neutral": 0, "negative": 0, "complaints": []}
            model_summary[model]["total"] += 1
            model_summary[model][res["predicted_sentiment"]] += 1
            
            # Collect complaints
            if res["predicted_sentiment"] == "negative":
                for asp in res["aspects_detected"]:
                    if asp["sentiment"] == "negative":
                        cat = asp["category"]
                        complaint_hotspots[cat] = complaint_hotspots.get(cat, 0) + 1
                        model_summary[model]["complaints"].append(f"{cat}: {asp['evidence']}")
                        
        # Generate actionable manager recommendations
        recommendations = []
        top_complaint_cats = sorted(complaint_hotspots.items(), key=lambda x: x[1], reverse=True)
        rec_templates = {
            "Performance": "Audit transmission and engine calibration; investigate low-end torque lags reported by drivers.",
            "Economy": "Re-evaluate ECU fuel mapping and aerodynamic drag coefficients to improve real-world fuel economy.",
            "Comfort": "Re-tune rear suspension damping and inspect seat cushion contouring for long-distance ride comfort.",
            "Technology": "Release OTA software patch to address infotainment input lag and Bluetooth disconnection bugs.",
            "Safety": "Enhance emergency braking calibration and address sensor blind-spot false positives.",
            "Design": "Upgrade cabin plastic trim materials to reduce squeaks and improve interior perceived quality.",
            "Ownership": "Enforce dealer service turn-around SLAs and reduce replacement parts procurement wait-times.",
            "Value": "Review variant feature packaging to ensure key convenience features are available at competitive price points."
        }
        
        for cat, count in top_complaint_cats[:4]:
            rec = rec_templates.get(cat, f"Address customer complaints regarding {cat} to mitigate churn.")
            recommendations.append({
                "category": cat,
                "complaint_count": count,
                "recommended_action": rec
            })
            
        return {
            "total_processed": len(results),
            "overall_sentiment": {
                "positive": sum(1 for r in results if r["predicted_sentiment"] == "positive"),
                "neutral": sum(1 for r in results if r["predicted_sentiment"] == "neutral"),
                "negative": sum(1 for r in results if r["predicted_sentiment"] == "negative"),
            },
            "brand_summary": brand_summary,
            "model_summary": model_summary,
            "top_complaint_hotspots": complaint_hotspots,
            "actionable_recommendations": recommendations,
            "predictions": results
        }

if __name__ == "__main__":
    predictor = AutoSensePredictor()
    sample = "The Mahindra Thar engine has great torque and looks rugged, but the ride suspension is stiff and bumpy on highways."
    res = predictor.predict_review(sample)
    print("Sample Prediction:")
    print(json.dumps(res, indent=2))
