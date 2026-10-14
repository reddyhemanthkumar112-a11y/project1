"""
Unit and integration tests for Citizen Complaint Management System.
"""

import unittest
import json
import os
import database
from app import app

class CitizenComplaintSystemTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config["TESTING"] = True
        self.client = app.test_client()
        # Ensure fresh clean sample data for each test run
        database.init_db(force_reseed=True)

    def test_database_initial_seed(self):
        """Verify that initial database seed creates 10 sample complaints across all categories."""
        complaints = database.get_complaints()
        self.assertEqual(len(complaints), 10)

        # Check all 5 categories are represented
        categories = {c["category"] for c in complaints}
        self.assertEqual(len(categories), 5)
        for cat in database.VALID_CATEGORIES:
            self.assertIn(cat, categories)

        # Check all 3 statuses are represented
        statuses = {c["status"] for c in complaints}
        self.assertIn("Submitted", statuses)
        self.assertIn("In progress", statuses)
        self.assertIn("Resolved", statuses)

    def test_api_get_complaints(self):
        """Test GET /api/complaints returns all complaints."""
        response = self.client.get("/api/complaints")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 10)

    def test_api_filter_by_category(self):
        """Test filtering complaints by category."""
        response = self.client.get("/api/complaints?category=Roads")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(all(c["category"] == "Roads" for c in data["complaints"]))
        self.assertGreaterEqual(len(data["complaints"]), 2)

    def test_api_filter_by_status(self):
        """Test filtering complaints by status."""
        response = self.client.get("/api/complaints?status=In%20progress")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(all(c["status"] == "In progress" for c in data["complaints"]))

    def test_api_filter_by_neighborhood(self):
        """Test filtering complaints by neighborhood."""
        response = self.client.get("/api/complaints?neighborhood=Downtown%20Central")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(all(c["neighborhood"] == "Downtown Central" for c in data["complaints"]))

    def test_api_search(self):
        """Test searching complaints by keyword."""
        response = self.client.get("/api/complaints?search=pothole")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data["complaints"]), 1)
        self.assertIn("pothole", data["complaints"][0]["title"].lower())

    def test_api_get_complaint_by_id(self):
        """Test retrieving a single complaint with its timeline history."""
        response = self.client.get("/api/complaints/CMP-2026-001")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        c = data["complaint"]
        self.assertEqual(c["id"], "CMP-2026-001")
        self.assertIn("history", c)
        self.assertGreaterEqual(len(c["history"]), 2)

    def test_api_get_complaint_not_found(self):
        """Test retrieving a non-existent complaint returns 404."""
        response = self.client.get("/api/complaints/CMP-2026-999")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data["success"])

    def test_api_create_complaint_success(self):
        """Test valid complaint creation."""
        payload = {
            "category": "Roads",
            "title": "Severe asphalt depression causing water pooling",
            "description": "The roadway has sunken 4 inches right beside the storm drain curb on 5th street.",
            "location": "5th Street & Washington Ave",
            "neighborhood": "Downtown Central",
            "contact_name": "Jane Citizen",
            "contact_email": "jane@example.org",
            "contact_phone": "555-4321"
        }
        response = self.client.post("/api/complaints", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("CMP-", data["complaint"]["id"])
        self.assertEqual(data["complaint"]["status"], "Submitted")
        self.assertEqual(data["complaint"]["responsible_department"], "Department of Transportation & Municipal Roads")

        # Verify it now appears in the complaints list
        verify_resp = self.client.get(f"/api/complaints/{data['complaint']['id']}")
        self.assertEqual(verify_resp.status_code, 200)

    def test_api_create_complaint_validation_errors(self):
        """Test validation error cases when submitting a complaint."""
        # Missing title
        resp = self.client.post("/api/complaints", json={
            "category": "Roads",
            "title": "",
            "description": "Adequate length description for test.",
            "location": "123 Main St"
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Title is required", resp.get_json()["error"])

        # Invalid category
        resp2 = self.client.post("/api/complaints", json={
            "category": "Spaceships",
            "title": "Valid title here",
            "description": "Adequate length description for test.",
            "location": "123 Main St"
        })
        self.assertEqual(resp2.status_code, 400)
        self.assertIn("Invalid category", resp2.get_json()["error"])

        # Short description
        resp3 = self.client.post("/api/complaints", json={
            "category": "Roads",
            "title": "Valid title here",
            "description": "Too short",
            "location": "123 Main St"
        })
        self.assertEqual(resp3.status_code, 400)
        self.assertIn("Description is required", resp3.get_json()["error"])

    def test_api_update_status(self):
        """Test advancing complaint status and recording notes in history."""
        # Update CMP-2026-004 from Submitted to In progress
        payload = {
            "status": "In progress",
            "actor": "Sanitation Dispatch Team",
            "notes": "Crew #3 assigned to clear overflowing bins."
        }
        response = self.client.post("/api/complaints/CMP-2026-004/status", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["complaint"]["status"], "In progress")

        # Check that the history contains this update
        history = data["complaint"]["history"]
        last_step = history[-1]
        self.assertEqual(last_step["status"], "In progress")
        self.assertEqual(last_step["actor"], "Sanitation Dispatch Team")
        self.assertEqual(last_step["notes"], "Crew #3 assigned to clear overflowing bins.")

    def test_api_stats(self):
        """Test summary statistics endpoint."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        stats = data["stats"]
        self.assertEqual(stats["total"], 10)
        self.assertEqual(stats["submitted"] + stats["in_progress"] + stats["resolved"], 10)
        self.assertEqual(len(stats["by_category"]), 5)

    def test_api_updates(self):
        """Test recent updates endpoint."""
        response = self.client.get("/api/updates?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["updates"]), 1)
        self.assertIn("notes", data["updates"][0])
        self.assertIn("complaint_id", data["updates"][0])

    def test_index_page(self):
        """Test HTML dashboard home page loads correctly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CivicPulse", response.data)
        self.assertIn(b"Report a Problem", response.data)
        self.assertIn(b"Neighborhood Map", response.data)

    def test_static_assets(self):
        """Verify static CSS, JS, and vendor files are accessible."""
        for path in [
            "/static/css/style.css",
            "/static/js/app.js",
            "/static/js/map.js",
            "/static/vendor/leaflet/leaflet.css",
            "/static/vendor/leaflet/leaflet.js"
        ]:
            with self.client.get(path) as resp:
                self.assertEqual(resp.status_code, 200, f"Static asset {path} failed to load.")
                self.assertGreater(len(resp.data), 0)


    def test_api_reset(self):
        """Test resetting database back to 10 sample complaints."""
        # Create a new dummy complaint
        self.client.post("/api/complaints", json={
            "category": "Roads",
            "title": "Temporary pothole for reset test",
            "description": "This is a temporary pothole to verify reset functionality.",
            "location": "123 Reset Avenue",
            "neighborhood": "Downtown Central"
        })
        self.assertEqual(len(database.get_complaints()), 11)

        # Trigger reset
        reset_resp = self.client.post("/api/reset")
        self.assertEqual(reset_resp.status_code, 200)
        self.assertEqual(len(database.get_complaints()), 10)

if __name__ == "__main__":
    unittest.main()

