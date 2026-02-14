from fastapi import FastAPI
import httpx
from fastapi.testclient import TestClient
import asyncio
import uvicorn

from app.api.routers.lots.lots_endpoints import router as lots_router
from app.api.routers.lots.lots_ws import router as ws_router

app = FastAPI(title="Auction API")
app.include_router(lots_router) 
app.include_router(ws_router) 

@app.get("/")
async def root():
    return {"status": "ok"}

#TODO remove testing
if __name__ == "__main__":
    # Запуск сервера для ручного тестування через Swagger або Postman
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000)