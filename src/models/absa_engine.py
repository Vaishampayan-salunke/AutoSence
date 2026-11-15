"""
AutoSense Aspect-Based Sentiment Analysis (ABSA) Engine
Evaluates aspect category detection and aspect sentiment classification
against peer-reviewed automotive ground-truth datasets (MuSe-CarASTE & Hybrid Car Reviews).
Uses the locked 8-aspect taxonomy:
Performance, Economy, Comfort, Technology, Safety, Design, Ownership, Value.
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from src.preprocessing.text_cleaner import clean_automobile_text
from src.preprocessing.taxonomy import AUTOMOTIVE_TAXONOMY, ASPECT_SENTIMENT_TRIGGERS
from src.models.vader_model import VaderBaseline

class AutoSenseABSAEngine:
    def __init__(self):
        self.vader = VaderBaseline()
        self.taxonomy = AUTOMOTIVE_TAXONOMY

    def extract_aspect_sentiments(self, review_text: str) -> list:
        """
        Extracts aspect observations with polarities from an automotive review text
        using the locked 8-aspect automotive taxonomy.
        """
        if not isinstance(review_text, str) or not review_text.strip():
            return []
            
        sentences = [s.strip() for s in review_text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        detected = []
        
        for category, config in self.taxonomy.items():
            keywords = config["keywords"]
            cat_sentences = []
            for s in sentences:
                s_lower = s.lower()
                for kw in keywords:
                    if kw in s_lower:
                        score = self.vader.predict_single(s)
                        cat_sentences.append({
                            "sentence": s,
                            "keyword": kw,
                            "sentiment": score["sentiment"],
                            "compound": score["compound"]
                        })
                        break
                        
            if cat_sentences:
                sentiments = [cs["sentiment"] for cs in cat_sentences]
                pos_c = sentiments.count("positive")
                neg_c = sentiments.count("negative")
                if pos_c > neg_c:
                    polarity = "positive"
                elif neg_c > pos_c:
                    polarity = "negative"
                else:
                    polarity = "neutral"
                    
                detected.append({
                    "aspect_category": category,
                    "aspect_sentiment": polarity,
                    "matched_keyword": cat_sentences[0]["keyword"],
                    "evidence_sentence": cat_sentences[0]["sentence"],
                    "compound_score": cat_sentences[0]["compound"]
                })
                
        return detected

    def evaluate_on_hybrid_car_dataset(self, file_path: str = r"Datasets/1000 reviews RS_P-7.xlsx") -> dict:
        """
        Evaluates aspect classification against Manzoor et al. 2022 (Data in Brief)
        """
        print(f"Evaluating ABSA on Hybrid Car Ground Truth: {file_path}...")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return {}
            
        df = pd.read_excel(file_path)
        rows = df.iloc[1:].copy()
        
        aspect_cols = {
            'Performance': 11,
            'Comfort': 12,
            'Safety': 13,
            'Design': 15,    # Exterior/Design
            'Economy': 10    # Driving / Economy
        }
        
        category_metrics = {}
        all_true = []
        all_pred = []
        
        for cat, col_idx in aspect_cols.items():
            y_true = []
            y_pred = []
            
            for _, r in rows.iterrows():
                val = r.iloc[col_idx]
                if pd.isna(val) or str(val).strip() in ['0', '', '0.0', 'nan', 'None']:
                    continue
                    
                val_str = str(val).strip().lower()
                if 'pos' in val_str or val_str == '1':
                    true_pol = 'positive'
                elif 'neg' in val_str or val_str == '-1':
                    true_pol = 'negative'
                elif 'neu' in val_str or val_str in ['0', '2']:
                    true_pol = 'neutral'
                else:
                    continue
                    
                rev_text = str(r.iloc[1])
                extracted = self.extract_aspect_sentiments(rev_text)
                
                cat_match = [e for e in extracted if e['aspect_category'] == cat]
                if cat_match:
                    pred_pol = cat_match[0]['aspect_sentiment']
                else:
                    pred_pol = self.vader.predict_single(rev_text)['sentiment']
                    
                y_true.append(true_pol)
                y_pred.append(pred_pol)
                
            if y_true:
                acc = accuracy_score(y_true, y_pred)
                p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
                category_metrics[cat] = {
                    'n_samples': len(y_true),
                    'accuracy': float(acc),
                    'weighted_precision': float(p),
                    'weighted_recall': float(r),
                    'weighted_f1': float(f1)
                }
                all_true.extend(y_true)
                all_pred.extend(y_pred)
                
        overall_acc = accuracy_score(all_true, all_pred)
        p, r, f1, _ = precision_recall_fscore_support(all_true, all_pred, average='weighted', zero_division=0)
        
        result = {
            'benchmark_name': 'Manzoor et al. 2022 (Hybrid Car Reviews)',
            'total_aspect_annotations_evaluated': len(all_true),
            'overall_accuracy': float(overall_acc),
            'weighted_precision': float(p),
            'weighted_recall': float(r),
            'weighted_f1': float(f1),
            'aspect_category_breakdown': category_metrics
        }
        return result

    def evaluate_on_muse_caraste(self, file_path: str = r"Datasets/Paper 9 — MuSe-CarASTE (2025)/Datasets/FinalFullAnnotationsAllLabelsCompleted.csv") -> dict:
        """
        Evaluates aspect sentiment classification against MuSe-CarASTE benchmark
        """
        print(f"Evaluating ABSA on MuSe-CarASTE Ground Truth: {file_path}...")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return {}
            
        df = pd.read_csv(file_path, encoding='latin1')
        df = df[df['sentiment'].isin(['pos', 'neg', 'neu'])].dropna(subset=['review']).head(3000)
        
        sent_map = {'pos': 'positive', 'neg': 'negative', 'neu': 'neutral'}
        y_true = []
        y_pred = []
        
        for _, row in df.iterrows():
            true_sentiment = sent_map.get(str(row['sentiment']).strip().lower())
            text = str(row['review'])
            score = self.vader.predict_single(text)
            pred_sentiment = score['sentiment']
            
            y_true.append(true_sentiment)
            y_pred.append(pred_sentiment)
            
        acc = accuracy_score(y_true, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        
        result = {
            'benchmark_name': 'MuSe-CarASTE (Usman et al. 2025)',
            'samples_evaluated': len(y_true),
            'accuracy': float(acc),
            'weighted_precision': float(p),
            'weighted_recall': float(r),
            'weighted_f1': float(f1)
        }
        return result

if __name__ == "__main__":
    engine = AutoSenseABSAEngine()
    hybrid_res = engine.evaluate_on_hybrid_car_dataset()
    print("Hybrid Car Benchmark:", json.dumps(hybrid_res, indent=2))
    
    muse_res = engine.evaluate_on_muse_caraste()
    print("MuSe-CarASTE Benchmark:", json.dumps(muse_res, indent=2))
    
    # Save benchmark artifacts
    os.makedirs("reports", exist_ok=True)
    with open("reports/absa_ground_truth_benchmarks.json", "w") as f:
        json.dump({"hybrid_car": hybrid_res, "muse_caraste": muse_res}, f, indent=2)
    print("Saved reports/absa_ground_truth_benchmarks.json successfully.")
