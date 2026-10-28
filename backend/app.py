"""
ToxiGuard Flask API.

- Serves the frontend (index.html, style.css, app.js) so only ONE process is needed.
- POST /predict   {"text": "..."}  -> toxicity verdict (English / Tamil / Telugu / Hindi,
  including Tanglish / Tenglish / Hinglish, and common leetspeak obfuscation).
- GET  /api/health -> {"status": "ok"}
"""
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from toxicity import ToxiGuard

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

print("Loading ToxiGuard model ...")
guard = ToxiGuard()
print("Model ready.")


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    # Only serve real files from frontend/ (style.css, app.js, images, ...)
    full_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(full_path):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"error": "not found"}), 404


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text field is required"}), 400
    result = guard.predict(text)
    return jsonify(result)


if __name__ == "__main__":
    print("\nToxiGuard running -> open http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
