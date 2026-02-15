from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from app.services.ws_lot_manager.ws_lot_manager import WSLotManager
from app.services.bid_manager.bid_manager import BidManager
from app.api.routers.lots.models.models_lots_endpoints import LotResponse
from app.core.logger.logger import AppLogger
from app.core.config.config import app_logger_settings

router = APIRouter(prefix="/ws/lots", tags=["WebSocket"])
ws_logger = AppLogger("WS_ENDPOINT", "ws_lot.log", app_logger_settings.LEVEL).get_instance()

async def get_ws_lot_manager() -> WSLotManager:
    return WSLotManager()
async def get_bid_manager() -> BidManager:
    return BidManager()

@router.websocket("/{lot_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    lot_id: int, 
    ws_manager: WSLotManager = Depends(get_ws_lot_manager),
    bid_manager: BidManager = Depends(get_bid_manager)
):
    # check bid manager if lot exists
    active_lots = await bid_manager.get_active_lots()
    if not any(lot.id == lot_id for lot in active_lots):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        ws_logger.warning(f"WS: Connection rejected. Lot {lot_id} not found.")
        return

    await ws_manager.connect(lot_id, websocket)
    ws_logger.info(f"Client connected to lot {lot_id}")
    
    try:
        while True:
            # Listen to clint if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(lot_id, websocket)
        ws_logger.info(f"Client disconnected from lot {lot_id}")