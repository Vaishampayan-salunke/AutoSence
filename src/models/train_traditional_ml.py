"""
AutoSense Traditional Machine Learning Training & Evaluation Module
Trains TF-IDF + Logistic Regression (Main Baseline), Linear SVM, and Multinomial Naive Bayes.
Strict Data Governance:
- TF-IDF Vectorizer is fit ONLY on Training data.
- Validation set is used for tuning/selection.
- Final performance is reported on the untouched Held-Out Test set.
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

def train_and_evaluate():
    print("=" * 70)
    print("AutoSense: Training Traditional ML Baselines (Phase 7)")
    print("=" * 70)
    
    # 1. Load Datasets
    train_df = pd.read_csv("Datasets/splits/train/train.csv")
    val_df = pd.read_csv("Datasets/splits/validation/val.csv")
    test_df = pd.read_csv("Datasets/splits/test/test.csv")
    
    X_train = train_df['review_text_processed'].fillna('')
    y_train = train_df['sentiment'].str.lower()
    
    X_val = val_df['review_text_processed'].fillna('')
    y_val = val_df['sentiment'].str.lower()
    
    X_test = test_df['review_text_processed'].fillna('')
    y_test = test_df['sentiment'].str.lower()
    
    labels = ['negative', 'neutral', 'positive']
    
    print(f"Data Summary: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
    
    # 2. Define Model Configurations
    models_config = {
        "autosense-tfidf-lr-v1": {
            "name": "TF-IDF + Logistic Regression (Main Baseline)",
            "pipeline": Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=12000, sublinear_tf=True, min_df=2)),
                ('clf', LogisticRegression(C=2.5, max_iter=1000, class_weight='balanced', random_state=42))
            ]),
            "family": "TRADITIONAL_ML",
            "is_main": True
        },
        "autosense-tfidf-nb-v1": {
            "name": "TF-IDF + Multinomial Naive Bayes",
            "pipeline": Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=12000, sublinear_tf=True, min_df=2)),
                ('clf', MultinomialNB(alpha=0.3))
            ]),
            "family": "TRADITIONAL_ML",
            "is_main": False
        },
        "autosense-tfidf-svm-v1": {
            "name": "TF-IDF + Linear SVM (Calibrated)",
            "pipeline": Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=12000, sublinear_tf=True, min_df=2)),
                ('clf', CalibratedClassifierCV(LinearSVC(C=1.2, random_state=42, class_weight='balanced', max_iter=2000)))
            ]),
            "family": "TRADITIONAL_ML",
            "is_main": False
        }
    }
    
    results = {}
    model_registry = {}
    
    # Registry path
    registry_path = r"V:\BDT\models\model_registry\model_registry.json"
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                model_registry = json.load(f)
        except Exception:
            model_registry = {}
            
    # Include VADER metrics in comparison if available
    vader_path = r"V:\BDT\models\vader\vader_evaluation.json"
    if os.path.exists(vader_path):
        with open(vader_path, 'r') as f:
            vader_eval = json.load(f)
            results["autosense-vader-baseline-v1"] = {
                "name": "VADER (Rule-Based Baseline)",
                "family": "RULE_BASED",
                "val_accuracy": None,
                "test_accuracy": vader_eval["metrics"]["accuracy"],
                "test_macro_f1": vader_eval["metrics"]["macro_f1"],
                "test_weighted_f1": vader_eval["metrics"]["weighted_f1"],
                "test_precision": vader_eval["metrics"]["macro_precision"],
                "test_recall": vader_eval["metrics"]["macro_recall"]
            }
            
    # 3. Train, Tune, and Evaluate Each Model
    for model_id, conf in models_config.items():
        print(f"\n--- Training {conf['name']} ({model_id}) ---")
        pipe = conf["pipeline"]
        
        # Fit on training data
        pipe.fit(X_train, y_train)
        
        # Validation Set Performance
        val_pred = pipe.predict(X_val)
        val_acc = accuracy_score(y_val, val_pred)
        val_f1 = precision_recall_fscore_support(y_val, val_pred, average='macro', zero_division=0)[2]
        print(f"Validation Score -> Accuracy: {val_acc:.4f}, Macro F1: {val_f1:.4f}")
        
        # Held-out Test Set Evaluation
        test_pred = pipe.predict(X_test)
        test_acc = accuracy_score(y_test, test_pred)
        prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, test_pred, average='macro', zero_division=0)
        prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(y_test, test_pred, average='weighted', zero_division=0)
        
        cm = confusion_matrix(y_test, test_pred, labels=labels).tolist()
        report = classification_report(y_test, test_pred, labels=labels, output_dict=True, zero_division=0)
        
        print(f"Test Score       -> Accuracy: {test_acc:.4f}, Macro F1: {f1_m:.4f}, Weighted F1: {f1_w:.4f}")
        
        # Save Joblib Pipeline Artifact
        artifact_path = os.path.join(r"V:\BDT\models\traditional_ml", f"{model_id}.joblib")
        joblib.dump(pipe, artifact_path)
        print(f"Saved artifact to {artifact_path}")
        
        # Record Comparison
        results[model_id] = {
            "name": conf["name"],
            "family": conf["family"],
            "val_accuracy": round(float(val_acc), 4),
            "val_macro_f1": round(float(val_f1), 4),
            "test_accuracy": round(float(test_acc), 4),
            "test_macro_f1": round(float(f1_m), 4),
            "test_weighted_f1": round(float(f1_w), 4),
            "test_precision": round(float(prec_m), 4),
            "test_recall": round(float(rec_m), 4),
            "confusion_matrix": cm,
            "classification_report": report
        }
        
        # Update Model Registry
        model_registry[model_id] = {
            "model_version": model_id,
            "model_name": conf["name"],
            "artifact_path": artifact_path,
            "is_active": conf.get("is_main", False),
            "test_accuracy": round(float(test_acc), 4),
            "test_macro_f1": round(float(f1_m), 4),
            "test_weighted_f1": round(float(f1_w), 4),
            "classes": labels
        }
        
    # Save Model Registry
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(model_registry, f, indent=2)
    print(f"\nModel Registry updated at {registry_path}")
    
    # Save Comparison Report
    comp_path = r"V:\BDT\experiments\experiment_01_baseline_comparison\model_comparison.json"
    os.makedirs(os.path.dirname(comp_path), exist_ok=True)
    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Full Experiment 1 Comparison saved to {comp_path}")
    
    # Print Comparison Table
    print("\n" + "=" * 80)
    print(f"{'Model Version':<26} | {'Accuracy':<10} | {'Macro F1':<10} | {'Weighted F1':<12}")
    print("-" * 80)
    for mid, r in results.items():
        print(f"{mid:<26} | {r['test_accuracy']:<10.4f} | {r['test_macro_f1']:<10.4f} | {r['test_weighted_f1']:<12.4f}")
    print("=" * 80)

if __name__ == '__main__':
    train_and_evaluate()
