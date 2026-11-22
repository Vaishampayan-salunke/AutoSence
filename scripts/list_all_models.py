import json

with open('frontend/dist/models_catalog.json', 'r', encoding='utf-8') as f:
    models = json.load(f)

print(f"Total models: {len(models)}")
for m in models:
    print(f"{m.get('brand')} -> {m.get('model')} ({m.get('body_type')})")
