#!/bin/bash

export DB_NAME="diplomska-db-testing"
export TESTING="TRUE"

echo "Starting FastAPI server..."
py -m source.main & SERVER_PID=$!

echo "Running the tests..."
pytest tests/test_students.py
pytest tests/test_companies.py
pytest tests/test_experiences.py
pytest tests/test_offers.py
pytest tests/test_applications.py
echo "All tests have completed"

echo "Stopping FastAPI server..."
kill $SERVER_PID
echo "Server stopped"