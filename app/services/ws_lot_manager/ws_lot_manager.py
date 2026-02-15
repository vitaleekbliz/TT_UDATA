from typing import Dict, List
from fastapi import WebSocket, status
from app.core.logger.logger import AppLogger
from app.core.config.config import app_logger_settings
from app.api.routers.lots.models.models_ws_lot import BidPlacedMessage


class WSLotManager:
    _ws_lot_manager_loger = AppLogger("WSLOTMANAGER", "sw_lot_manager.log", app_logger_settings.LEVEL).get_instance()
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the object only if it doesn't exist
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Run once
        if self._initialized:
            return
        
        self._ws_lot_manager_loger.info("Created ws lot manager instance")
        
        # Dictionary : {lot_id: [список_websocket_клієнтів]}
        self._active_connections: Dict[int, List[WebSocket]] = {}

        self._initialized = True

    async def connect(self, lot_id: int, websocket: WebSocket):
        await websocket.accept()
        #TODO test if server should do memory clean ups 
        if lot_id not in self._active_connections:
            self._active_connections[lot_id] = []

        self._ws_lot_manager_loger.info(f"Accepted client websocket on lot {lot_id}")

        self._active_connections[lot_id].append(websocket)

    async def disconnect(self, lot_id: int, websocket: WebSocket):
        if lot_id in self._active_connections:

            if(websocket in self._active_connections[lot_id]):
                self._active_connections[lot_id].remove(websocket)
                self._ws_lot_manager_loger.info(f"Disconnected client from websocket on lot {lot_id}")

    async def broadcast_to_lot(self, lot_id: int, message: BidPlacedMessage):
        """Send message to all active listeners of the lot"""
        if lot_id in self._active_connections:
            message_data = message.model_dump()
            self._ws_lot_manager_loger.debug(f"Sending listening clients on lot {lot_id}, message : {message_data}")

            for connection in self._active_connections[lot_id]:
                await connection.send_json(message_data)

    async def close_lot_connections(self, lot_id: int):
        """Close all connections for lot"""
        if lot_id in self._active_connections:
            connections = self._active_connections[lot_id][:]  # Copy list
            for connection in connections:
                try:
                    close_message = BidPlacedMessage(
                        type="bid_closed",
                        lot_id=lot_id,
                        bidder="system",
                        amount=0
                    )
                    message_data = close_message.model_dump()
                    await connection.send_json(message_data)
                    await connection.close(code=status.WS_1000_NORMAL_CLOSURE)
                except Exception as e:
                    self._ws_lot_manager_loger.error(f"Error closing WS: {e}")

            # Clear connections list for lot
            del self._active_connections[lot_id]
            self._ws_lot_manager_loger.info(f"WS: All connections for lot {lot_id} closed.")