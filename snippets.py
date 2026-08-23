##########################
### OBJECTIVES 1 and 2 ###
##########################

# Step 3: Implement Custom Logging Filter to Scrub PII
# - Add a PIIFilter class to intercept and sanitize log records - see PIIFilter.py
# - Attach the filter to your logger instance

logger = logging.getLogger("AppLogger")
logger.addFilter(PIIFilter())

# Step 4: Implement Secure Exception Handlers
# - In app.py, disable Flask's debug mode and register a generic 500 exception handler - see disable_flask_PII_mode.py
# - Ensure app.run(debug=False) is set at the bottom of app.py

# Step 5: Verify Secure Error Handling and Logging Remediations
# - Stop the running Flask application in the Terminal by pressing Ctrl + C
# - Restart the updated application: python3 app.py
# - Execute the test request again from the second Terminal window - see the curl call in commands.sh
# - Verify that the user-facing output no longer shows any Python stack trace or internal exception details - see safe_output.json
# - Check the application terminal logs and verify that sensitive password data was scrubbed and replaced with redacted placeholders

##########################
### OBJECTIVE 3 ##########
##########################

# Step 3: Observe Stack Trace and Environment Variable Leakage
# - Open the Terminal inside VS Code or the standalone Terminal Emulator.
# - Navigate to the application folder (see commands.sh): cd /home/ubuntu/fastapi-secure-handling
# - Start the FastAPI service using uvicorn (see commands.sh): uvicorn main:app --reload --port 8000
# - Open a second terminal window or tab and issue a request that triggers the unhandled exception: curl -i http://127.0.0.1:8000/items/error
# - Inspect the HTTP response payload. 
#   Observe that the server returns an HTTP 500 status code with a raw exception message exposing internal application secrets:
HTTP/1.1 500 Internal Server Error
content-type: text/plain; charset=utf-8

Internal Server Error: Database connection failed! Env Context -> DB: postgresql://admin:SuperSecretPass123!@db.internal:5432/prod_db | Key: sk_live_998877665544332211


# Step 4: Implement Custom Global Error Handler in FastAPI
# - Open main.py in Visual Studio Code.
# - Add imports for Request, logging, and HTMLResponse or JSONResponse: see main.py
# - Save the changes to main.py.
!!! JSONResponse seems to be missing. TODO


# Step 5: Verify Secure Error Rendering Remediations
# - If Uvicorn was running with --reload, it automatically reloaded the application. If not, restart Uvicorn in your terminal session:
#   uvicorn main:app --port 8000
# - Re-run the test request from the second terminal window:
#   curl -i http://127.0.0.1:8000/items/error
# - Verify that the response body now outputs the generic, styled HTML error page without 
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

# Unexpected error handler
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Log the full exception internally for debugging
    logger.error(f"Internal system error occurred: {error}", exc_info=True)
    
    # Return a safe, generic response to the user
    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }
    return jsonify(response), 500
