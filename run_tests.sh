#!/bin/bash

ENV_FILE=".env"

sed -i 's/^TESTING=.*/TESTING=TRUE/' $ENV_FILE
echo "Set testing parameter to TRUE"

echo "Running the tests..."
pytest source/test_applications.py
pytest source/test_companies.py
pytest source/test_experiences.py
pytest source/test_offers.py
pytest source/test_students.py
echo "All tests have completed"

sed -i 's/^TESTING=.*/TESTING=FALSE/' $ENV_FILE
echo "Reverted testing parameter to FALSE"