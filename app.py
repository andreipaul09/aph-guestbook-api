from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os

app = Flask(__name__)
CORS(app)  # Allow all origins so your Vercel site can talk to this

# ── Supabase Config ──────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://npvzjokretciicpchwfp.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5wdnpqb2tyZXRjaWljcGNod2ZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NjY1MTUsImV4cCI6MjA4NzM0MjUxNX0.ACbGcPD9g_RJ1ZxEZZnv6OCMSnQCZmApHBsw_GFesG8")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Health Check ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "message": "APH Guestbook API is running 🚀",
        "author": "Andrei Paul F. Hospital",
        "endpoints": {
            "GET /guestbook": "Get all messages",
            "POST /guestbook": "Post a new message"
        }
    })

# ── GET /guestbook ────────────────────────────────────────
# Returns all guestbook messages from Supabase
@app.route("/guestbook", methods=["GET"])
def get_messages():
    try:
        response = supabase.table("guestbook") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()

        return jsonify({
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ── POST /guestbook ───────────────────────────────────────
# Inserts a new message into Supabase
@app.route("/guestbook", methods=["POST"])
def post_message():
    try:
        body = request.get_json()

        # Validate input
        if not body:
            return jsonify({"success": False, "error": "No data provided"}), 400

        name = body.get("name", "").strip()
        message = body.get("message", "").strip()

        if not name:
            return jsonify({"success": False, "error": "Name is required"}), 400
        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        if len(name) > 50:
            return jsonify({"success": False, "error": "Name too long (max 50 chars)"}), 400
        if len(message) > 300:
            return jsonify({"success": False, "error": "Message too long (max 300 chars)"}), 400

        # Insert into Supabase
        response = supabase.table("guestbook").insert({
            "name": name,
            "message": message
        }).execute()

        return jsonify({
            "success": True,
            "data": response.data[0] if response.data else None,
            "message": "Message posted successfully!"
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
