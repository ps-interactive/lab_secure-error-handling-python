##########################
### OBJECTIVES 1 and 2 ###
##########################

# Step 2: Implement Custom Logging Filter to Scrub PII
# - Add a PIIFilter class to intercept and sanitize log records - see PIIFilter.py

# Secure Global Error Handler (Hides Tracebacks from Client)
class PIIFilter(logging.Filter):
    SENSITIVE_KEYS = {"password", "api_key", "secret", "ssn", "credit_card"}

    def filter(self, record):
        # 1. Scrub dictionary payloads
        if isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        # 2. Scrub string messages
        elif isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)
            
        # 3. Scrub exception message/tracebacks if present
        if record.exc_text:
            record.exc_text = self._sanitize_string(record.exc_text)

        return True

    def _sanitize_string(self, text):
        # Basic check to redact sensitive strings or keys
        for key in self.SENSITIVE_KEYS:
            if key in text.lower():
                return "[REDACTED SENSITIVE CONTENT]"
        return text

    def _sanitize_dict(self, data):
        cleaned_data = copy.deepcopy(data)
        for key, value in cleaned_data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                cleaned_data[key] = "[REDACTED]"
            elif isinstance(value, dict):
                cleaned_data[key] = self._sanitize_dict(value)
        return cleaned_data


# Attach the filter to your logger instance
logger.addFilter(PIIFilter())

# Step 3: Implement Secure Exception Handlers
# Here we deal with application traces that reveal sensitive data
# - In app.py, disable Flask's debug mode and register a generic 500 exception handler - see disable_flask_PII_mode.py
# - Ensure app.run(debug=False) is set at the bottom of app.py

# Secure Global Error Handler (Hides Tracebacks from Client)
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Log internal error safely
    logger.error(
        f"An unexpected internal error occurred: {error}", exc_info=True
    )

    # Return sanitized generic response to user
    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
    }
    return jsonify(response), 500


# Step 4: Verify Secure Error Handling and Logging Remediations
# - Stop the running Flask application in the Terminal by pressing Ctrl + C
# - Restart the updated application: python3 app.py
# - Execute the test request again from the second Terminal window - see the curl call in commands.sh
# - Verify that the user-facing output no longer shows any Python stack trace or internal exception details - see safe_output.json
# - Check the application terminal logs and verify that sensitive password data was scrubbed and replaced with redacted placeholders

##########################
### OBJECTIVE 3 ##########
##########################

# Step 1: Observe Stack Trace and Environment Variable Leakage
# - Open the Terminal inside VS Code or the standalone Terminal Emulator.
# - Navigate to the application folder (see commands.sh): cd /home/ubuntu/fastapi-secure-handling
# - Start the FastAPI service using uvicorn (see commands.sh): uvicorn main:app --reload --port 8000
# - Open a second terminal window or tab and issue a request that triggers the unhandled exception: curl -i http://127.0.0.1:8000/items/error
# - Inspect the HTTP response payload. 
#   Observe that the server returns an HTTP 500 status code with a raw exception message exposing internal application secrets:
HTTP/1.1 500 Internal Server Error
content-type: text/plain; charset=utf-8

Internal Server Error: Database connection failed! Env Context -> DB: postgresql://admin:SuperSecretPass123!@db.internal:5432/prod_db | Key: sk_live_998877665544332211


# Step 2: 
# Add imports
import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

# Step 3:
# Configure internal secure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("SecurityLogger")

# Step 4:
# Implement Custom Global Error Handler in FastAPI
# - Open main.py in Visual Studio Code.
# - Add imports for Request, logging, and HTMLResponse or JSONResponse: see main.py
# - Save the changes to main.py.

# Custom Exception Handler to capture all unhandled broad exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exact exception internally for diagnostic debugging
    logger.error(f"Unhandled Exception at {request.url.path}: {exc}", exc_info=True)
    
    # Render a safe custom HTML error page for the end user without internal details
    custom_error_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Internal Server Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f8f9fa; }
            h1 { color: #dc3545; }
            p { color: #6c757d; }
        </style>
    </head>
    <body>
        <h1>An Unexpected Error Occurred</h1>
        <p>Our engineering team has been notified. Please try again later.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=custom_error_html, status_code=500)

# Step 5: Remove the credentials from the RuntimeError message
# Replace this: raise RuntimeError(f"Database connection failed! Env Context -> DB: {db_url} | Key: {secret}")
# with this:
raise RuntimeError(f"Database connection failed!")

# Step 6: Verify Secure Error Rendering Remediations
# - If Uvicorn was running with --reload, it automatically reloaded the application. If not, restart Uvicorn in your terminal session:
#   uvicorn main:app --port 8000
# - Re-run the test request from the second terminal window:
#   curl -i http://127.0.0.1:8000/items/error
# - Verify that the response body now outputs the generic, styled HTML error page WITHOUT: 
#   - leaking database URIs, 
#   - API keys, or 
#   - Raw stack trace lines:
HTTP/1.1 500 Internal Server Error
content-type: text/html; charset=utf-8

    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Internal Server Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f8f9fa; }
            h1 { color: #dc3545; }
            p { color: #6c757d; }
        </style>
    </head>
    <body>
        <h1>An Unexpected Error Occurred</h1>
        <p>Our engineering team has been notified. Please try again later.</p>
    </body>
    </html>
# - Check the application log in the first terminal window to verify that the complete traceback and 
#   error context were recorded securely on the backend server for troubleshooting purposes.
