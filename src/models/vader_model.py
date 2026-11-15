"""
AutoSense VADER Rule-Based Baseline Model
Uses NLTK / vaderSentiment SentimentIntensityAnalyzer with documented threshold conventions.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import json
import os
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

class VaderBaseline:
    def __init__(self, pos_threshold=0.05, neg_threshold=-0.05):
        self.analyzer = SentimentIntensityAnalyzer()
        self.pos_threshold = pos_threshold
        self.neg_threshold = neg_threshold
        self.version = "autosense-vader-baseline-v1"
        
    def predict_single(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            return {
                "sentiment": "neutral",
                "compound": 0.0,
                "scores": {"pos": 0.0, "neu": 1.0, "neg": 0.0, "compound": 0.0}
            }
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= self.pos_threshold:
            sentiment = "positive"
        elif compound <= self.neg_threshold:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "compound": round(compound, 4),
            "scores": scores
        }
        
    def predict(self, texts: list) -> list:
        return [self.predict_single(t)["sentiment"] for t in texts]

    def evaluate(self, test_df_path: str = r"Datasets/splits/test/test.csv") -> dict:
        df = pd.read_csv(test_df_path)
        y_true = df['sentiment'].str.lower().tolist()
        texts = df['review_text_processed'].fillna('').tolist()
        
        y_pred = self.predict(texts)
        
        acc = accuracy_score(y_true, y_pred)
        prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        
        labels = ['negative', 'neutral', 'positive']
        report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
        
        results = {
            "model_version": self.version,
            "model_type": "Rule-based Lexicon (VADER)",
            "evaluation_set": "Held-Out Test Set",
            "sample_size": len(df),
            "pos_threshold": self.pos_threshold,
            "neg_threshold": self.neg_threshold,
            "metrics": {
                "accuracy": round(float(acc), 4),
                "macro_f1": round(float(f1_macro), 4),
                "weighted_f1": round(float(f1_w), 4),
                "macro_precision": round(float(prec_macro), 4),
                "macro_recall": round(float(rec_macro), 4),
                "weighted_precision": round(float(prec_w), 4),
                "weighted_recall": round(float(rec_w), 4)
            },
            "confusion_matrix": {
                "labels": labels,
                "matrix": cm
            },
            "per_class_report": report
        }
        
        # Save evaluation results
        out_path1 = r"V:\BDT\models\vader\vader_evaluation.json"
        out_path2 = r"V:\BDT\experiments\experiment_01_baseline_comparison\vader_metrics.json"
        
        os.makedirs(os.path.dirname(out_path1), exist_ok=True)
        os.makedirs(os.path.dirname(out_path2), exist_ok=True)
        
        with open(out_path1, 'w') as f:
            json.dump(results, f, indent=2)
        with open(out_path2, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"VADER Evaluation on Test Set ({len(df)} samples):")
        print(f"  Accuracy:    {acc:.4f}")
        print(f"  Macro F1:    {f1_macro:.4f}")
        print(f"  Weighted F1: {f1_w:.4f}")
        print(f"Saved artifacts to {out_path1} and {out_path2}")
        return results

if __name__ == '__main__':
    vader = VaderBaseline()
    vader.evaluate()
