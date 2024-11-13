#!/bin/bash

ENV_FILE=".env"

sed -i 's/^TESTING=.*/TESTING=TRUE/' $ENV_FILE
echo "Set testing parameter to TRUE"

echo "Starting FastAPI server..."
uvicorn source.main:app --reload > /dev/null 2>&1 &
SERVER_PID=$!

echo "Running the tests..."
pytest source/test_applications.py
pytest source/test_companies.py
pytest source/test_experiences.py
pytest source/test_offers.py
pytest source/test_students.py
echo "All tests have completed"

echo "Stopping FastAPI server..."
echo "Server process PID: $SERVER_PID"
kill $SERVER_PID
echo "Server stopped"