from typing import Dict, List
from fastapi import WebSocket
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
        self.active_connections: Dict[int, List[WebSocket]] = {}

        self._initialized = True

    async def connect(self, lot_id: int, websocket: WebSocket):
        await websocket.accept()
        #TODO test if server should do memory clean ups 
        if lot_id not in self.active_connections:
            self.active_connections[lot_id] = []

        self._ws_lot_manager_loger.info(f"Accepted client websocket on lot {lot_id}")

        self.active_connections[lot_id].append(websocket)

    def disconnect(self, lot_id: int, websocket: WebSocket):
        if lot_id in self.active_connections:
            self._ws_lot_manager_loger.info(f"Disconnected client from websocket on lot {lot_id}")

            self.active_connections[lot_id].remove(websocket)

    async def broadcast_to_lot(self, lot_id: int, message: BidPlacedMessage):
        """Send message to all active listeners of the lot"""
        if lot_id in self.active_connections:
            message_data = message.model_dump()
            self._ws_lot_manager_loger.debug(f"Sending listening clients on lot {lot_id}, message : {message_data}")

            for connection in self.active_connections[lot_id]:
                await connection.send_json(message_data)
