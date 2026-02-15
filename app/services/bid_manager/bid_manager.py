from typing import Dict, List
from app.services.lot.lot import Lot
from app.services.lot.status import LotStatus
from app.core.logger.logger import AppLogger
from app.services.bid_manager.errors import *
from app.core.config.config import app_logger_settings
from app.api.routers.lots.models.models_lots_endpoints import LotResponse
import asyncio


class BidManager:
    _bid_manager_loger = AppLogger("BIDMANAGER", "bid_manager.log", app_logger_settings.FILE_LEVEL).get_instance()
    _instance = None
    _monitor_task = None

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
        
        self._bid_manager_loger.info("Created bid manager instance")

        #TODO create closed lots arrays for non active lots
        # Right way would be to remove lot when its finished and insert it to database
        self._active_lots: Dict[int, Lot] = {}

        # Launch monitor
        if self._monitor_task is None:
            self._monitor_task = asyncio.create_task(self._background_monitor())

        self._initialized = True

    def stop_monitor(self):
        if self._monitor_task:
            self._monitor_task.cancel()

    async def _background_monitor(self):
        """Background task for closing lots"""
        self._bid_manager_loger.info("BidManager: Background monitor started.")
        #TODO create another class "LotScheduleChecker" to avoid circular dependancy
        # best way to solve this is to pass callback funtion to call WSLotManager when lot is closed to close all connections on lot
        #crutch here
        from app.api.routers.lots.lots_ws import WSLotManager

        try:
            while True:

                lot_ids_to_close = [
                    lot.get_id() for lot in self._active_lots.values() 
                    if lot.check_status() != LotStatus.RUNNING
                ]

                for lot_id in lot_ids_to_close:
                    self._bid_manager_loger.info(f"Monitor: Closing expired lot {lot_id}")

                    self._close_lot(lot_id)

                    # Close client connection to lot
                    await WSLotManager().close_lot_connections(lot_id)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            self._bid_manager_loger.info("Monitor: Background task cancelled.")
        except Exception as e:
            self._bid_manager_loger.error(f"Monitor: Error in background task: {e}")


    def _close_lot(self, lot_id: int):
        # Return none if lot not found in active lots
        lot = self._active_lots.pop(lot_id, None)

        if lot:
            self._bid_manager_loger.info(f"Lot {lot_id} successfully closed and removed.")
            # Save to DB
        else:
            self._bid_manager_loger.warning(f"Attempted to close lot {lot_id}, but it was already removed.")

        #Delete lot if needed
        # Caution. Lot after closing can have other statuses : Pending payment...
        # Check app.services.lot.status for that



    async def get_lot_response_model(self, lot_id: int)->LotResponse:
        lot = self._active_lots.get(lot_id)

        if(not lot):
            self._bid_manager_loger.error(f"Error: Lot {lot_id} not found.")
            raise BidManagerLotIsNotFoundError(f"Error: Lot {lot_id} not found.")
        
        return lot.get_lot_response_model()
        

    async def create_lot(self, starting_price: int = 10, start_lifeduration:int = 30, lifeduration_on_update:int = 10, bid_step:int = 5) -> LotResponse:
        """Creates a lot and returns its unique ID."""
        self._bid_manager_loger.info("Creating lot")

        new_lot = Lot(starting_price, start_lifeduration, lifeduration_on_update, bid_step)
        self._active_lots[new_lot.get_id()] = new_lot

        return new_lot.get_lot_response_model()

    async def bid_on_lot(self, lot_id: int, amount: int) -> bool:
        """
        Logic for placing a bid. 
        Returns True if successful, raises error or returns False if not.
        """
        lot = self._active_lots.get(lot_id)
        
        if not lot:
            self._bid_manager_loger.error(f"Error: Lot {lot_id} not found.")
            raise BidManagerLotIsNotFoundError(f"Error: Lot {lot_id} not found.")
            
        lot.place_bid(amount)
            
        # Update the lot state
        self._bid_manager_loger.info(f"BIdManager Success: New high bid of {amount} on lotID='{lot.get_id()}' Returning true")
        return True

    async def get_active_lots(self) -> List[LotResponse]:
        active_lots: List[LotResponse] = []

        #append running lots 
        for lot in self._active_lots.values():
            if(lot.check_status() == LotStatus.RUNNING):
                active_lots.append(lot.get_lot_response_model())
        
        self._bid_manager_loger.info(f"Found {len(active_lots)} active lots out of {len(self._active_lots)}")

        #I dont like python one lines xD
        #return [lot for lot in self._active_lots.values() if lot.check_status() == LotStatus.RUNNING]

        return active_lots