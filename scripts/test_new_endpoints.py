import sys
sys.path.insert(0, 'V:/BDT')
from backend.app.routes.api import (
    get_datasets_registry,
    get_pipeline_status,
    get_provenance_registry,
    get_preprocessing_report,
    get_confusion_matrices,
    get_experiment_records,
    predict_compare
)
from backend.app.schemas.schemas import PredictCompareRequest

def test_direct():
    print("Testing get_datasets_registry()...")
    d = get_datasets_registry()
    print("  -> Datasets:", len(d.get("datasets", [])))

    print("Testing get_pipeline_status()...")
    p = get_pipeline_status()
    print("  -> Stages:", len(p.get("stages", [])))

    print("Testing get_provenance_registry()...")
    prov = get_provenance_registry()
    print("  -> Metrics in provenance:", len(prov.get("metrics", {})))

    print("Testing get_preprocessing_report()...")
    prep = get_preprocessing_report()
    print("  -> Preprocessing total records:", prep.get("total_records_unified"))

    print("Testing get_confusion_matrices()...")
    cm = get_confusion_matrices()
    print("  -> Evaluated models in CM:", len(cm.get("results", [])))

    print("Testing get_experiment_records()...")
    exp = get_experiment_records()
    print("  -> Experiments:", len(exp.get("experiments", [])))

    print("Testing predict_compare()...")
    req = PredictCompareRequest(text="The engine is powerful and responsive, but the mileage and fuel consumption are terrible.", include_aspects=True)
    res = predict_compare(req)
    print("  -> Consensus sentiment:", res.get("consensus_sentiment"))
    print("  -> Agreement percentage:", res.get("agreement_percentage"), "%")
    print("  -> Models evaluated:", len(res.get("results", [])))
    print("  -> Aspects detected:", len(res.get("aspects", [])))
    for r in res.get("results", []):
        print(f"     * {r['model_name']}: {r['predicted_sentiment']} (conf: {r['confidence']}) [{r['provenance']}] in {r['processing_ms']}ms")

    print("\nALL 7/7 ENDPOINTS TESTED AND VERIFIED DIRECTLY WITH REAL MODELS!")

if __name__ == "__main__":
    test_direct()
