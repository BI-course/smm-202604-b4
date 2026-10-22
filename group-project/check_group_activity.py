"""Verify saved artifacts through API, Streamlit forms and Gradio callbacks."""
import hashlib
import json
import os
from pathlib import Path

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
from api import app
from predictions import SPECS, PHARMACY, example_payload, input_schema, predict

ROOT = Path(__file__).resolve().parent


def main():
    from streamlit.testing.v1 import AppTest
    samples, schemas, results = {}, {}, {}
    client = app.test_client()
    for key, spec in SPECS.items():
        payload = example_payload(key)
        samples[key] = payload
        response = client.post(f"/api/v1/models/{key}/predictions", json=payload)
        assert response.status_code == 200, (key, response.get_data(as_text=True))
        results[key] = response.get_json()
        assert results[key] == predict(key, payload)
        assert client.post(f"/api/v1/models/{key}/predictions", json={}).status_code == 400
        fields = input_schema(key)
        if key == "pharmacy-recommender":
            fields = [{"name": "cart", "label": "Products in basket (comma separated)",
                       "default": ", ".join(payload["cart"]), "options": None},
                      {"name": "top_n", "label": "Maximum suggestions", "default": 3, "options": None}]
        schemas[key] = {"title": spec["title"], "description": spec["description"], "fields": fields}
        print(f"API PASS: {key}: {json.dumps(results[key])}", flush=True)
    probabilities = results["insurance-fraud-classifier"]["class_probabilities"]
    assert abs(sum(probabilities.values()) - 1) < .00001
    assert results["bank-account-segmenter"]["assigned_cluster"] in [0, 1, 2]
    recommendations = results["pharmacy-recommender"]["recommendations"]
    assert recommendations
    assert client.post("/api/v1/models/pharmacy-recommender/predictions", json={"cart": ["unknown"]}).status_code == 400
    assert client.post("/api/v1/models/pharmacy-recommender/predictions", json={"cart": ["Baby Lotion"], "top_n": -1}).status_code == 400
    assert client.get("/demo").status_code == 200
    (ROOT / "examples.json").write_text(json.dumps(samples, indent=2), encoding="utf-8")
    (ROOT / "frontend" / "schemas.json").write_text(json.dumps(schemas, indent=2), encoding="utf-8")

    ui = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not ui.exception, [item.message for item in ui.exception]
    assert len(ui.tabs) == 4
    for i, key in enumerate(SPECS):
        ui.button[i].click().run(timeout=60)
        assert not ui.exception, [item.message for item in ui.exception]
        assert ui.session_state[key + "result"]["output"] == results[key]
        print(f"STREAMLIT PASS: {key}", flush=True)

    import gradio_app
    for key, (callback, fields) in gradio_app.CALLBACKS.items():
        payload = dict(samples[key])
        if key == "pharmacy-recommender":
            payload["cart"] = ", ".join(payload["cart"])
        assert callback(*[payload[field] for field in fields]) == results[key]
        print(f"GRADIO PASS: {key}", flush=True)
    manifest = json.loads((ROOT / "artifact-manifest.json").read_text(encoding="utf-8"))
    for name, expected_hash in manifest["model_sha256"].items():
        assert hashlib.sha256((ROOT / "model" / name).read_bytes()).hexdigest() == expected_hash
    (ROOT / "validation-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("All group checks passed. Same saved artifacts used across the interfaces.", flush=True)


if __name__ == "__main__":
    main()
