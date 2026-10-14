"""
Citizen Complaint Management System
Flask backend providing REST APIs and civic dashboard views.
"""

import os
from flask import Flask, jsonify, request, render_template, send_from_directory
import database

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = "civicpulse-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Ensure database is initialized on startup
database.init_db(force_reseed=False)

@app.route("/")
def index():
    """Serves the main Citizen Complaint Portal dashboard."""
    return render_template(
        "index.html",
        categories=database.VALID_CATEGORIES,
        statuses=database.VALID_STATUSES,
        neighborhoods=database.NEIGHBORHOODS,
        departments=database.DEPARTMENT_MAP
    )

@app.route("/api/complaints", methods=["GET"])
def api_get_complaints():
    """Returns a filtered list of complaints."""
    category = request.args.get("category")
    status = request.args.get("status")
    neighborhood = request.args.get("neighborhood")
    search = request.args.get("search")
    sort_by = request.args.get("sort", "newest")

    complaints = database.get_complaints(
        category=category,
        status=status,
        neighborhood=neighborhood,
        search=search,
        sort_by=sort_by
    )
    return jsonify({
        "success": True,
        "count": len(complaints),
        "complaints": complaints
    })

@app.route("/api/complaints/<complaint_id>", methods=["GET"])
def api_get_complaint(complaint_id):
    """Returns detailed information for a single complaint including its audit timeline."""
    complaint = database.get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({
            "success": False,
            "error": f"Complaint with ID '{complaint_id}' was not found."
        }), 404

    return jsonify({
        "success": True,
        "complaint": complaint
    })

@app.route("/api/complaints", methods=["POST"])
def api_create_complaint():
    """Validates and creates a new citizen complaint."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    created, err = database.create_complaint(data)
    if err:
        return jsonify({
            "success": False,
            "error": err
        }), 400

    return jsonify({
        "success": True,
        "message": "Complaint submitted successfully.",
        "complaint": created
    }), 201

@app.route("/api/complaints/<complaint_id>/status", methods=["POST"])
def api_update_status(complaint_id):
    """Updates the status and appends a department response note."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    new_status = data.get("status")
    actor = data.get("actor", "Department Officer")
    notes = data.get("notes", "")

    if not new_status:
        return jsonify({
            "success": False,
            "error": "Field 'status' is required."
        }), 400

    updated, err = database.update_complaint_status(complaint_id, new_status, actor, notes)
    if err:
        status_code = 404 if "not found" in err.lower() else 400
        return jsonify({
            "success": False,
            "error": err
        }), status_code

    return jsonify({
        "success": True,
        "message": f"Complaint status successfully updated to '{new_status}'.",
        "complaint": updated
    })

@app.route("/api/stats", methods=["GET"])
def api_get_stats():
    """Returns complaint counts and category breakdown."""
    neighborhood = request.args.get("neighborhood")
    stats = database.get_stats(neighborhood=neighborhood)
    return jsonify({
        "success": True,
        "stats": stats
    })

@app.route("/api/updates", methods=["GET"])
def api_get_updates():
    """Returns recent status changes and department responses."""
    limit = request.args.get("limit", default=10, type=int)
    neighborhood = request.args.get("neighborhood")
    updates = database.get_recent_updates(limit=limit, neighborhood=neighborhood)
    return jsonify({
        "success": True,
        "count": len(updates),
        "updates": updates
    })

@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Resets the database back to clean realistic sample data."""
    database.init_db(force_reseed=True)
    stats = database.get_stats()
    return jsonify({
        "success": True,
        "message": "Database reset to realistic sample complaints.",
        "stats": stats
    })

if __name__ == "__main__":
    # Run the server on port 5000 (accessible on localhost)
    print("=" * 60)
    print("Starting Citizen Complaint Management System on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
