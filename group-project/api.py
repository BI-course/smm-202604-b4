"""The same group API can run locally, in Docker, and on Render."""
from flask import Flask, jsonify, request
from predictions import SPECS, predict

app = Flask(__name__, static_folder="frontend", static_url_path="/demo-assets")


@app.get("/")
def home():
    return jsonify(status="ready", endpoints=[f"/api/v1/models/{key}/predictions" for key in SPECS])


@app.get("/demo")
def demo():
    return app.send_static_file("index.html")


@app.post("/api/v1/models/<key>/predictions")
def prediction(key):
    if key not in SPECS:
        return jsonify(error="Unknown model", available_models=list(SPECS)), 404
    try:
        result = predict(key, request.get_json(silent=True))
    except (ValueError, TypeError, KeyError) as error:
        return jsonify(error=str(error)), 400
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
