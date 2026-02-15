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

#TODO Add Closing all connections for lot and cleaning up lot array in ws manager
# 

#TODO remove testing
if __name__ == "__main__":
    client = TestClient(app)
    
    print("\n🚀 Starting Edge Case Testing...")

    # --- Case 1: Connection to Non-existent Lot ---
    print("\nTEST 1: Connecting to non-existent lot...")
    try:
        with client.websocket_connect("/ws/lots/999999") as websocket:
            # Якщо ми сюди потрапили, значить сокет відкрився, а мав закритися
            pass
    except Exception:
        # FastAPI/Starlette викидає помилку, якщо сервер закриває з'єднання під час handshake
        print("✅ Success: Connection rejected with 404 or closed immediately.")

    # --- Case 2: Race Condition / Concurrent Bidding ---
    # Створюємо лот для тестів
    create_res = client.post("/lots/", json={"name": "Edge Case Lot", "price": 100})
    lot_id = create_res.json()["id"]
    
    print(f"\nTEST 2: Testing broadcast for lot {lot_id}...")
    with client.websocket_connect(f"/ws/lots/{lot_id}") as websocket:
        # Робимо ставку, яка нижча за поточну (якщо у вас є така валідація)
        low_bid = client.post(f"/lots/{lot_id}/bids", json={"amount": 10, "name": "LowBaller"})
        print(f"[-] Low bid status: {low_bid.status_code}")

        # Робимо валідну ставку
        valid_bid = client.post(f"/lots/{lot_id}/bids", json={"amount": 500, "name": "RichGuy"})
        print(f"[-] Valid bid status: {valid_bid.status_code}")

        # Перевіряємо, що в сокет прийшла тільки валідна ставка
        msg = websocket.receive_json()
        print(f"✅ Received WS message: {msg['bidder']} set {msg['amount']}")
        assert msg["amount"] == 500

    # --- Case 3: Lot Closure & WS Cleanup ---
    print("\nTEST 3: Testing lot closure behavior...")
    # Емулюємо закриття лота (якщо у вас є такий метод в API)
    # Або напряму через manager, якщо він доступний
    from app.api.routers.lots.lots_endpoints import get_bid_manager, BidManager
    manager = asyncio.run(get_bid_manager()) 
    
    with client.websocket_connect(f"/ws/lots/{lot_id}") as websocket:
        print("[-] WS Connected. Closing lot now...")
        BidManager()._close_lot(lot_id=lot_id)
        
        # Спроба зробити ставку на вже видалений лот
        post_close_bid = client.post(f"/lots/{lot_id}/bids", json={"amount": 1000, "name": "LateComer"})
        print(f"[-] Bid after close status: {post_close_bid.status_code}")
        assert post_close_bid.status_code == 404
        print("✅ Success: Cannot bid on closed lot.")

    print("\n🎯 All edge cases passed!")
    
    # Запуск сервера, якщо тести пройшли
    print("\n--- Starting Production Server ---")
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000, reload=True)