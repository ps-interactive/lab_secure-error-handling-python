from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id == "error":
        # HTTPException is natively handled by FastAPI and will not output a traceback
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    
    return {"item_id": item_id, "status": "active"}