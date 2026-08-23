#!/bin/bash

python3 app.py

curl -X POST http://127.0.0.1:5000/user/update \
     -H "Content-Type: application/json" \
     -d '{"username": "johndoe", "password": "SuperSecretPassword123", "trigger_error": true}'


# - Navigate to the application folder: 
cd /home/ubuntu/fastapi-secure-handling

# - Start the FastAPI service using uvicorn: 
uvicorn main:app --reload --port 8000

# - Open a second terminal window or tab and issue a request that triggers the unhandled exception: 
curl -i http://127.0.0.1:8000/items/error


# If Uvicorn was running with --reload, it automatically reloaded the application. If not, restart Uvicorn in your terminal session:
uvicorn main:app --port 8000

# Re-run the test request from the second terminal window:
curl -i http://127.0.0.1:8000/items/error

# Start ASGI web server
python3 -m uvicorn main:app --reload --port 8000

# Test with cURL request
curl -i http://127.0.0.1:8000/items/error

