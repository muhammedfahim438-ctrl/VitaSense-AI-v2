"""
VitaSense AI - routes/chatbot.py
Flask route for POST /chat
Receives user message, detects topic, returns educational response.
Saves conversation to chat_history table.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from chatbot_model import get_response
from models import save_chat

chatbot_bp = Blueprint("chatbot", __name__)


# ─── POST /chat ───────────────────────────────────────────────────────────────

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    """
    Accepts JSON: { "message": "user question here" }
    Returns full chatbot response with topic and title.
    """
    try:
        # Parse input
        if request.is_json:
            data = request.get_json(force=True) or {}
        else:
            data = request.form.to_dict()

        user_message = str(data.get("message", "")).strip()

        # Validate
        if not user_message:
            return jsonify({
                "success":  False,
                "error":    "Message cannot be empty.",
            }), 400

        if len(user_message) > 500:
            return jsonify({
                "success":  False,
                "error":    "Message is too long. Please keep it under 500 characters.",
            }), 400

        # Get chatbot response
        result = get_response(user_message)

        # Save to DB
        save_chat(
            user_message = user_message,
            bot_response = result["response"],
            topic        = result["topic"],
        )

        return jsonify({
            "success":  True,
            "topic":    result["topic"],
            "title":    result["title"],
            "response": result["response"],
            "found":    result["found"],
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error":   f"Server error: {str(e)}",
        }), 500


# ─── GET /chat/history ────────────────────────────────────────────────────────

@chatbot_bp.route("/chat/history", methods=["GET"])
def chat_history():
    """Returns the last N chat messages. Default limit = 50."""
    try:
        from models import get_db_connection
        limit = int(request.args.get("limit", 50))
        conn  = get_db_connection()
        cur   = conn.cursor()
        cur.execute("""
            SELECT id, created_at, user_message, bot_response, topic
            FROM chat_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        return jsonify({"success": True, "history": rows}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─── GET /chat/topics ─────────────────────────────────────────────────────────

@chatbot_bp.route("/chat/topics", methods=["GET"])
def list_topics():
    """Returns all 20 available chatbot topic titles — used for quick-reply buttons."""
    from chatbot_model import TOPICS
    topics = [
        {"key": key, "title": data["title"]}
        for key, data in TOPICS.items()
    ]
    return jsonify({"success": True, "topics": topics}), 200