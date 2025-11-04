import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from flask import send_from_directory
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__, static_folder='.', static_url_path='')
# Allow requests from file:// and localhost for local development
CORS(app, resources={r"/*": {"origins": "*"}})


# -----------------------------
# Configuration
# -----------------------------
# Insert your Gemini API key via environment (see .env.example)
API_KEY = os.getenv("GEMINI_API_KEY", "") or ""

# Choose a lightweight, cost‑effective model for chat (configurable via env GEMINI_MODEL)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
API_VERSION = os.getenv("GEMINI_API_VERSION", "v1")  # use v1 by default


def _endpoint_for_model(model_name: str) -> str:
    return (
        f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{model_name}:generateContent"
    )


def call_gemini(prompt: str) -> str:
    if not API_KEY:
        return "Gemini API key is not set. Please set GEMINI_API_KEY or edit app.py."

    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    # Try primary model and fallbacks when 404 occurs
    candidate_models = []
    primary = (GEMINI_MODEL or "").strip() or "gemini-1.5-flash"
    candidate_models.append(primary)
    for fallback in ("gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"):
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    last_error = None
    for model in candidate_models:
        try:
            response = requests.post(
                _endpoint_for_model(model),
                params={"key": API_KEY},
                headers=headers,
                data=json.dumps(payload),
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    continue
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
                return text or "I couldn't generate a response right now. Please try again."

            # If 404, try next model; otherwise return error
            if response.status_code == 404:
                last_error = response
                continue
            try:
                data = response.json()
            except Exception:
                data = {"error": response.text}
            return f"Gemini error ({response.status_code}): {data}"
        except Exception as e:
            last_error = e
            continue

    if last_error is not None:
        if isinstance(last_error, requests.Response):
            try:
                data = last_error.json()
            except Exception:
                data = {"error": last_error.text}
            return f"Gemini error ({last_error.status_code}): {data}"
        return f"Gemini error: {str(last_error)}"
    return "I couldn't generate a response right now. Please try again."


@app.route("/health", methods=["GET"])
def health() -> tuple:
    resp = jsonify({"ok": True})
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp, 200


@app.route("/chat", methods=["POST"])
def chat() -> tuple:
    try:
        data = request.get_json(force=True) or {}
        user_message = (data.get("message") or "").strip()
        if not user_message:
            return jsonify({"error": "Missing 'message'"}), 400

        reply = call_gemini(user_message)
        resp = jsonify({"reply": reply})
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        return resp, 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# -----------------------------
# Frontend routes (serve static files)
# -----------------------------
@app.route("/")
def root() -> any:
    return send_from_directory(app.static_folder, "index.html")


# Optional explicit routes (static handler will also serve these directly)
@app.route("/chat.html")
def page_chat() -> any:
    return send_from_directory(app.static_folder, "chat.html")


@app.route("/reminders.html")
def page_reminders() -> any:
    return send_from_directory(app.static_folder, "reminders.html")


@app.route("/about.html")
def page_about() -> any:
    return send_from_directory(app.static_folder, "about.html")


@app.route("/privacy.html")
def page_privacy() -> any:
    return send_from_directory(app.static_folder, "privacy.html")


@app.route("/config.js")
def config_js():
    firebase_config = {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
    }
    body = (
        "window.AURA_CONFIG = window.AURA_CONFIG || {};\n"
        f"window.AURA_CONFIG.firebaseConfig = {json.dumps(firebase_config)};\n"
    )
    resp = app.response_class(body, mimetype='application/javascript')
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

if __name__ == "__main__":
    # You can also set host="0.0.0.0" if needed
    app.run(host="0.0.0.0", port=5000, debug=True)


