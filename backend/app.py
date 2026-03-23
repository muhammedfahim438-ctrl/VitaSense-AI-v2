"""
VitaSense AI - app.py
Main Flask application entry point.
Registers all blueprints, enables CORS, initialises DB, runs on port 5000.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

from models import init_db
from routes.predict import predict_bp
from routes.chatbot import chatbot_bp

# ─── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)  # Allow all origins — needed for Live Server (different port)

# ─── Register blueprints ──────────────────────────────────────────────────────

app.register_blueprint(predict_bp)
app.register_blueprint(chatbot_bp)

# ─── Health check ─────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status":  "running",
        "app":     "VitaSense AI",
        "version": "2.0",
        "endpoints": {
            "predict":          "POST /predict",
            "history":          "GET  /predictions/history",
            "dashboard_stats":  "GET  /dashboard/stats",
            "chat":             "POST /chat",
            "chat_topics":      "GET  /chat/topics",
            "chat_history":     "GET  /chat/history",
        }
    }), 200


# ─── Initialise DB + Run ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  VitaSense AI — Starting Server")
    print("=" * 50)

    # Create DB tables if they don't exist
    init_db()

    print("  Server : http://localhost:5000")
    print("  CORS   : Enabled (all origins)")
    print("=" * 50)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )