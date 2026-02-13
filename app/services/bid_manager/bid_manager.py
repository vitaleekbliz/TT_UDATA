from typing import Dict, List, Optional
from app.services.lot.lot import Lot
from app.services.lot.status import LotStatus
from app.core.logger.logger import AppLogger
import logging
from app.services.bid_manager.errors import *
from app.core.config.config import app_logger_settings, auction_settings

class BidManager:
    _bid_manager_loger = AppLogger("BIDMANAGER", "bid_manager.log", app_logger_settings.LEVEL).get_instance()
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the object only if it doesn't exist
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Виконуємо код лише якщо він ще не запускався
        if self._initialized:
            return
        
        #TODO create active lots and closed lots arrays
        self.lots: Dict[int, Lot] = {}
        self._bid_manager_loger.info("Created bid manager instance")

        self._initialized = True

    def create_lot(self, starting_price: int = 10, start_lifeduration:int = 30, lifeduration_on_update:int = 10, bid_step:int = 5) -> int:
        """Creates a lot and returns its unique ID."""
        self._bid_manager_loger.info("Creating lot")

        #USED config for values
        start_lifeduration = auction_settings.START_LIFE_DURATION
        lifeduration_on_update = auction_settings.UPDATE_LIFE_DURATION
        bid_step = auction_settings.MIN_BID_INCREMENT

        new_lot = Lot(starting_price, start_lifeduration, lifeduration_on_update, bid_step)
        lot_id = new_lot.get_id()
        self.lots[lot_id] = new_lot
        return lot_id

    def bid_on_lot(self, lot_id: int, amount: int) -> bool:
        """
        Logic for placing a bid. 
        Returns True if successful, raises error or returns False if not.
        """
        lot = self.lots.get(lot_id)
        
        if not lot:
            self._bid_manager_loger.error(f"Error: Lot {lot_id} not found.")
            raise BidManagerLotIsNotFoundError(f"Error: Lot {lot_id} not found.")
            
        lot.place_bid(amount)
            
        # Update the lot state
        self._bid_manager_loger.info(f"BIdManager Success: New high bid of {amount} on lotID='{lot.get_id()}' Returning true")
        return True

    def get_active_lots(self) -> List[Lot]:
        active_lots: List[Lot] = []

        #append running lots 
        for lot in self.lots.values():
            if(lot.check_status() == LotStatus.RUNNING):
                active_lots.append(lot)

        
        self._bid_manager_loger.info(f"Found {len(active_lots)} active lots out of {len(self.lots)}")

        return active_lots


#TODO remove debug main function
if __name__ == "__main__":
    print("=== Starting BidManager Testing ===\n")
    a = BidManager()
    b = BidManager()
    a.create_lot()
    a.create_lot()
    b.create_lot()
    print(len(b.get_active_lots()))
    print(a is b)
