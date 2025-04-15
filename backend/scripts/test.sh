#!/bin/bash

# Build and start the containers
docker-compose up -d --build

# Wait for the database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Install test dependencies
docker-compose exec backend pip install -r tests/requirements.txt

# Run the tests
echo "Running tests..."
docker-compose exec backend python -m pytest tests/test_api.py -v

# Stop the containers
echo "Tests completed. Stopping containers..."
docker-compose down 