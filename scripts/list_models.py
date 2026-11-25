import json

with open('frontend/dist/autosense_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

for i, m in enumerate(bundle.get('models_catalog', [])):
    print(f"{i+1}. {m.get('brand')} - {m.get('model')} [{m.get('body_type')}]")
