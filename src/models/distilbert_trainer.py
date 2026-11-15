"""
AutoSense DistilBERT Transformer Fine-Tuning & Evaluation Module
Fine-tunes DistilBERT for ternary automotive sentiment classification.
Saves model weights, tokenizer, and evaluation metrics for Experiment 2 (E2).
"""
import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from torch.optim import AdamW
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix

class AutomobileReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=64):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        
    def __len__(self):
        return len(self.texts)
        
    def __getitem__(self, item):
        text = str(self.texts[item])
        inputs = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )
        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[item], dtype=torch.long)
        }

def train_and_evaluate_distilbert(epochs=1, batch_size=16, lr=3e-5):
    print("=" * 70)
    print("AutoSense: DistilBERT Transformer Fine-Tuning (Phase 8)")
    print("=" * 70)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Execution Target Device: {device}")
    
    # Label mappings
    label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
    id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
    
    # Multi-threaded CPU acceleration
    torch.set_num_threads(4)
    
    # 1. Load data
    train_df = pd.read_csv(r"V:\BDT\datasets\splits\train\train.csv")
    val_df = pd.read_csv(r"V:\BDT\datasets\splits\validation\val.csv")
    test_df = pd.read_csv(r"V:\BDT\datasets\splits\test\test.csv")
    
    # Stratified CPU feasibility sample for local execution without GPU
    train_subset = train_df.sample(n=min(300, len(train_df)), random_state=42).reset_index(drop=True)
    val_subset = val_df.sample(n=min(100, len(val_df)), random_state=42).reset_index(drop=True)
    
    model_name = 'distilbert-base-uncased'
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    
    train_dataset = AutomobileReviewDataset(
        texts=train_subset['review_text_processed'].fillna('').tolist(),
        labels=[label2id[s] for s in train_subset['sentiment']],
        tokenizer=tokenizer
    )
    val_dataset = AutomobileReviewDataset(
        texts=val_subset['review_text_processed'].fillna('').tolist(),
        labels=[label2id[s] for s in val_subset['sentiment']],
        tokenizer=tokenizer
    )
    test_dataset = AutomobileReviewDataset(
        texts=test_df['review_text_processed'].fillna('').tolist(),
        labels=[label2id[s] for s in test_df['sentiment']],
        tokenizer=tokenizer
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    # 2. Initialize Model
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=3,
        id2label=id2label,
        label2id=label2id,
        local_files_only=True
    )
    model.to(device)
    
    optimizer = AdamW(model.parameters(), lr=lr)
    
    print(f"Beginning training for {epochs} epoch(s) on {len(train_subset)} samples...")
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for step, batch in enumerate(train_loader):
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
            if (step + 1) % 5 == 0 or (step + 1) == len(train_loader):
                print(f"  Epoch {epoch+1} | Step {step+1}/{len(train_loader)} | Loss: {loss.item():.4f}", flush=True)
                
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1} Completed | Average Loss: {avg_loss:.4f}", flush=True)
        
    # 3. Validation Evaluation
    model.eval()
    val_preds, val_targets = [], []
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1).cpu().tolist()
            val_preds.extend(preds)
            val_targets.extend(batch['labels'].tolist())
            
    val_acc = accuracy_score(val_targets, val_preds)
    val_f1 = precision_recall_fscore_support(val_targets, val_preds, average='macro', zero_division=0)[2]
    print(f"\nValidation Score -> Accuracy: {val_acc:.4f}, Macro F1: {val_f1:.4f}")
    
    # 4. Held-Out Test Set Evaluation
    test_preds, test_targets, test_probs = [], [], []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=1).cpu().tolist()
            preds = torch.argmax(outputs.logits, dim=1).cpu().tolist()
            test_preds.extend(preds)
            test_probs.extend(probs)
            test_targets.extend(batch['labels'].tolist())
            
    test_acc = accuracy_score(test_targets, test_preds)
    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(test_targets, test_preds, average='macro', zero_division=0)
    prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(test_targets, test_preds, average='weighted', zero_division=0)
    
    target_names = ['negative', 'neutral', 'positive']
    report = classification_report(test_targets, test_preds, target_names=target_names, output_dict=True, zero_division=0)
    cm = confusion_matrix(test_targets, test_preds).tolist()
    
    print(f"Test Score       -> Accuracy: {test_acc:.4f}, Macro F1: {f1_m:.4f}, Weighted F1: {f1_w:.4f}")
    
    # 5. Save Artifacts
    output_dir = r"V:\BDT\models\distilbert\autosense-distilbert-v1"
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved DistilBERT model weights and tokenizer to {output_dir}")
    
    distilbert_results = {
        "model_version": "autosense-distilbert-v1",
        "model_name": "Fine-Tuned DistilBERT (Transformer)",
        "base_model": model_name,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "device": str(device),
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
    
    # Save evaluation metric json
    eval_json_path = os.path.join(output_dir, "distilbert_evaluation.json")
    with open(eval_json_path, 'w', encoding='utf-8') as f:
        json.dump(distilbert_results, f, indent=2)
        
    exp2_path = r"V:\BDT\experiments\experiment_01_baseline_comparison\distilbert_metrics.json"
    with open(exp2_path, 'w', encoding='utf-8') as f:
        json.dump(distilbert_results, f, indent=2)
        
    # Update Model Registry
    registry_path = r"V:\BDT\models\model_registry\model_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {}
        
    registry["autosense-distilbert-v1"] = {
        "model_version": "autosense-distilbert-v1",
        "model_name": "Fine-Tuned DistilBERT (Transformer)",
        "artifact_path": output_dir,
        "is_active": True,
        "test_accuracy": round(float(test_acc), 4),
        "test_macro_f1": round(float(f1_m), 4),
        "test_weighted_f1": round(float(f1_w), 4),
        "classes": target_names
    }
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
        
    print(f"Updated model registry at {registry_path}")
    print("=" * 70)

if __name__ == '__main__':
    train_and_evaluate_distilbert(epochs=1, batch_size=16, lr=3e-5)
