#!/bin/bash

ENV_FILE=".env"

export DB_NAME="diplomska-db-testing"
export TESTING="TRUE"

echo "Starting FastAPI server..."
uvicorn source.main:app # > /dev/null 2>&1 &
SERVER_PID=$!

echo "Running the tests..."
# pytest tests/test_applications.py
# pytest tests/test_companies.py
# pytest tests/test_experiences.py
# pytest tests/test_offers.py
pytest tests/test_students.py::test_student_update -vs

echo "All tests have completed"

echo "Stopping FastAPI server..."
kill $SERVER_PID
echo "Server stopped"