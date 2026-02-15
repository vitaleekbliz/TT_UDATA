from fastapi import FastAPI

from app.api.routers.lots.lots_endpoints import router as lots_router
from app.api.routers.lots.lots_ws import router as ws_router

app = FastAPI(title="Auction API")
app.include_router(lots_router) 
app.include_router(ws_router) 

@app.get("/")
async def root():
    return {"status": "ok"}
