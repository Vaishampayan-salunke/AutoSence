import os
import sys
import json
import sqlite3
import pandas as pd

def audit():
    report = {}
    
    # 1. Datasets
    unified_csv = "V:/BDT/Datasets/normalized/automobile_reviews_unified_12000.csv"
    train_csv = "V:/BDT/Datasets/splits/train/train.csv"
    val_csv = "V:/BDT/Datasets/splits/val/val.csv"
    test_csv = "V:/BDT/Datasets/splits/test/test.csv"
    
    report["datasets"] = {
        "unified_exists": os.path.exists(unified_csv),
        "unified_rows": len(pd.read_csv(unified_csv)) if os.path.exists(unified_csv) else 0,
        "train_rows": len(pd.read_csv(train_csv)) if os.path.exists(train_csv) else 0,
        "val_rows": len(pd.read_csv(val_csv)) if os.path.exists(val_csv) else 0,
        "test_rows": len(pd.read_csv(test_csv)) if os.path.exists(test_csv) else 0
    }
    
    # Check split overlap
    if os.path.exists(train_csv) and os.path.exists(test_csv):
        train_df = pd.read_csv(train_csv)
        test_df = pd.read_csv(test_csv)
        overlap = set(train_df['review_id']).intersection(set(test_df['review_id']))
        report["datasets"]["train_test_id_overlap"] = len(overlap)
    
    # 2. Database
    db_path = "V:/BDT/bigdata/mysql/autosense_local.db"
    report["database"] = {"exists": os.path.exists(db_path)}
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        report["database"]["tables"] = {}
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t};")
            report["database"]["tables"][t] = cursor.fetchone()[0]
        conn.close()
        
    # 3. Models
    models_dir = "V:/BDT/models"
    report["models"] = {
        "lr_exists": os.path.exists(f"{models_dir}/traditional_ml/autosense-tfidf-lr-v1.joblib"),
        "svm_exists": os.path.exists(f"{models_dir}/traditional_ml/autosense-tfidf-svm-v1.joblib"),
        "nb_exists": os.path.exists(f"{models_dir}/traditional_ml/autosense-tfidf-nb-v1.joblib"),
        "distilbert_safetensors": os.path.exists(f"{models_dir}/distilbert/autosense-distilbert-v1/model.safetensors"),
        "vader_eval_exists": os.path.exists(f"{models_dir}/vader/vader_evaluation.json"),
        "model_registry_exists": os.path.exists(f"{models_dir}/model_registry/model_registry.json")
    }
    
    # 4. Reports & Experiments
    report["reports"] = {
        "analytics_cache": os.path.exists("V:/BDT/reports/analytics_cache.json"),
        "absa_benchmarks": os.path.exists("V:/BDT/reports/absa_ground_truth_benchmarks.json"),
        "model_comparison": os.path.exists("V:/BDT/experiments/experiment_01_baseline_comparison/model_comparison.json"),
        "pipeline_benchmark": os.path.exists("V:/BDT/experiments/experiment_03_pipeline_benchmark/pipeline_benchmark_results.json")
    }

    print(json.dumps(report, indent=2))
    with open("V:/BDT/reports/audit_phase_a.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    audit()
