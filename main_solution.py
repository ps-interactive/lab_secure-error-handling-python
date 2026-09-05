import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# Configure internal secure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("SecurityLogger")

app = FastAPI()

os.environ["DATABASE_URL"] = "postgresql://admin:SuperSecretPass123!@db.internal:5432/prod_db"
os.environ["SECRET_KEY"] = "sk_live_998877665544332211"

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

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id == "error":
        db_url = os.environ.get("DATABASE_URL")
        secret = os.environ.get("SECRET_KEY")
        raise RuntimeError(f"Database connection failed! Env Context -> DB: {db_url} | Key: {secret}")
    
    return {"item_id": item_id, "status": "active"}
