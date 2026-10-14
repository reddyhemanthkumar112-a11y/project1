#!/usr/bin/env bash
echo "================================================================="
echo " CivicPulse - Citizen Complaint Management System"
echo "================================================================="
echo ""
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
echo ""
echo "Running automated verification tests..."
python3 test_app.py
echo ""
echo "Starting application server at http://127.0.0.1:5000..."
echo "(Press Ctrl+C to stop the server)"
echo ""
python3 app.py
