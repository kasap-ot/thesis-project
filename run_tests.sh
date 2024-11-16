#!/bin/bash

ENV_FILE=".env"

ORIGINAL_DB_NAME=$(grep '^DB_NAME=' $ENV_FILE | cut -d '=' -f 2)
sed -i 's/^DB_NAME=.*/DB_NAME=diplomska-db-testing/' $ENV_FILE
echo "Changed DB_NAME to diplomksa-db-testing"

ORIGINAL_TESTING_VALUE=$(grep '^TESTING=' $ENV_FILE | cut -d '=' -f 2)
sed -i 's/^TESTING=.*/TESTING=TRUE/' $ENV_FILE
echo "Set testing parameter to TRUE"

echo "Starting FastAPI server..."
uvicorn source.main:app --reload > /dev/null 2>&1 &
SERVER_PID=$!

echo "Running the tests..."
pytest tests/test_applications.py
pytest tests/test_companies.py
pytest tests/test_experiences.py
pytest tests/test_offers.py
pytest tests/test_students.py
echo "All tests have completed"

echo "Stopping FastAPI server..."
kill $SERVER_PID
echo "Server stopped"

sed -i "s/^DB_NAME=.*/DB_NAME=$ORIGINAL_DB_NAME/" $ENV_FILE
echo "Reverted DB_NAME to $ORIGINAL_DB_NAME"

sed -i "s/^TESTING=.*/TESTING=$ORIGINAL_TESTING_VALUE/" $ENV_FILE
echo "Reverted TESTING to $ORIGINAL_TESTING_VALUE"