import json

bundle_path = 'frontend/dist/autosense_bundle.json'
with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

with open('frontend/dist/models_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

bundle['models_catalog'] = catalog

with open(bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f)

print(f"[SUCCESS] Synced models catalog with images into {bundle_path}")
