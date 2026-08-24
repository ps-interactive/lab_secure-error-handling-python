import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Simulated system secrets loaded into environment variables
os.environ["DATABASE_URL"] = "postgresql://admin:SuperSecretPass123!@db.internal:5432/prod_db"
os.environ["SECRET_KEY"] = "sk_live_998877665544332211"

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id == "error":
        db_url = os.environ.get("DATABASE_URL")
        secret = os.environ.get("SECRET_KEY")
        raise RuntimeError(f"Database connection failed! Env Context -> DB: {db_url} | Key: {secret}")
    
    return {"item_id": item_id, "status": "active"}