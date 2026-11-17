import json, os

bundle_path = 'V:/BDT/frontend/dist/autosense_bundle.json'
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

for key, path in [
    ('provenance', 'V:/BDT/reports/provenance.json'),
    ('confusion_matrices', 'V:/BDT/reports/confusion_matrices.json'),
    ('experiment_records', 'V:/BDT/reports/experiment_records.json'),
    ('preprocessing_report', 'V:/BDT/reports/preprocessing_report.json'),
    ('dataset_manifest', 'V:/BDT/reports/dataset_manifest.json')
]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            bundle[key] = json.load(f)
            print(f"Added {key} to bundle.")

with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, indent=2)

print(f"[SUCCESS] Updated autosense_bundle.json. Total keys: {list(bundle.keys())}")
print(f"File size: {os.path.getsize(bundle_path)} bytes")
