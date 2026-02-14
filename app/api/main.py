from fastapi import FastAPI
import httpx
from fastapi.testclient import TestClient
import asyncio

from app.api.routers.lots.lots_endpoints import router as lots_router

app = FastAPI(title="Auction API")
app.include_router(lots_router) 

@app.get("/")
async def root():
    return {"status": "ok"}

# --- БЛОК ТЕСТУВАННЯ ---
if __name__ == "__main__":
    print("=== Starting API Integration Tests ===\n")
    
    # Створюємо клієнт для тестування
    with TestClient(app) as client:
        
        # 1. Тест: Створення лота (POST /lots/)
        print("Test 1: Creating a new lot...")
        # Оскільки у вашому коді create_lot не приймає body, шлемо пустий POST
        response = client.post("/lots/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            lot_id = response.json().get("id")
            
            # 2. Тест: Отримання списку активних лотів (GET /lots/)
            print("\nTest 2: Listing active lots...")
            list_res = client.get("/lots/")
            print(f"Active lots count: {len(list_res.json())}")

            # 3. Тест: Ставка на лот (POST /lots/{id}/bids)
            print(f"\nTest 3: Placing a bid on lot {lot_id}...")
            # Передаємо суму згідно з вашою схемою BidRequest
            bid_payload = {"amount": 150, "name": "Dmitro"} 
            bid_res = client.post(f"/lots/{lot_id}/bids", json=bid_payload)
            print(f"Status: {bid_res.status_code}")
            print(f"Response: {bid_res.json()}")

            # 4. Тест: Занизька ставка (Очікуємо 400 Error)
            print("\nTest 4: Placing a low bid (Should fail)...")
            low_bid_payload = {"amount": 10, "name":"Vasia"}
            bad_res = client.post(f"/lots/{lot_id}/bids", json=low_bid_payload)
            print(f"Status: {bad_res.status_code} (Expected 400)")
            print(f"Detail: {bad_res.json().get('detail')}")

    print("\n=== All Integration Tests Completed ===")