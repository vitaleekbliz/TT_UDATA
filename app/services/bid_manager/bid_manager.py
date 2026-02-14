from typing import Dict, List, Optional
from app.services.lot.lot import Lot
from app.services.lot.status import LotStatus
from app.core.logger.logger import AppLogger
import logging
import time
from app.services.bid_manager.errors import *
from app.core.config.config import app_logger_settings
from app.api.routers.lots.models.models_lots_endpoints import LotResponse


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

    async def get_lot_response_model(self, lot_id: int)->LotResponse:
        lot = self.lots.get(lot_id)

        if(not lot):
            self._bid_manager_loger.error(f"Error: Lot {lot_id} not found.")
            raise BidManagerLotIsNotFoundError(f"Error: Lot {lot_id} not found.")
        
        return lot.get_lot_response_model()
        

    async def create_lot(self, starting_price: int = 10, start_lifeduration:int = 30, lifeduration_on_update:int = 10, bid_step:int = 5) -> LotResponse:
        """Creates a lot and returns its unique ID."""
        self._bid_manager_loger.info("Creating lot")

        #USED config for values
        # start_lifeduration = auction_settings.START_LIFE_DURATION
        # lifeduration_on_update = auction_settings.UPDATE_LIFE_DURATION
        # bid_step = auction_settings.MIN_BID_INCREMENT

        new_lot = Lot(starting_price, start_lifeduration, lifeduration_on_update, bid_step)
        self.lots[new_lot.get_id()] = new_lot
        
        return new_lot.get_lot_response_model()

    async def bid_on_lot(self, lot_id: int, amount: int) -> bool:
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

    async def get_active_lots(self) -> List[LotResponse]:
        active_lots: List[LotResponse] = []

        #append running lots 
        for lot in self.lots.values():
            if(lot.check_status() == LotStatus.RUNNING):
                active_lots.append(lot.get_lot_response_model())
        
        self._bid_manager_loger.info(f"Found {len(active_lots)} active lots out of {len(self.lots)}")

        #I dont like python one lines xD
        #return [lot for lot in self.lots.values() if lot.check_status() == LotStatus.RUNNING]

        return active_lots


#TODO remove debug main function
if __name__ == "__main__":
    print("=== Starting BidManager Testing ===\n")
    
    # 1. Перевірка Singleton
    a = BidManager()
    b = BidManager()
    
    print(f"Is 'a' the same instance as 'b'? {a is b}")  # Має бути True
    print(f"Manager A ID: {id(a)}")
    print(f"Manager B ID: {id(b)}\n")

    # 2. Створення лотів через різні змінні
    # Використовуємо значення з вашого AuctionSettings
    a.create_lot(
        starting_price=100
    )
    a.create_lot(
        starting_price=50
    )
    b.create_lot(
        starting_price=200
    )

    # 3. Перевірка кількості та ID
    active_lots = b.get_active_lots()
    print(f"Total active lots in 'b': {len(active_lots)}") # Має бути 3
    
    print("\n--- Current Lots State ---")
    for lot in active_lots:
        # Перевіряємо, чи ID збільшуються: 1, 2, 3
        print(f"Lot ID: {lot.get_id()} | Price: {lot._current_price}")

    # 4. Тест автоматичного завершення (через ваші 3 секунди в конфігу)
    print(f"\nWaiting {auction_settings.START_LIFE_DURATION + 2} seconds for lots to expire...")
    time.sleep(auction_settings.START_LIFE_DURATION -  1 )
    a.bid_on_lot(2, 1000)
    time.sleep(auction_settings.START_LIFE_DURATION - 1)
    #a.bid_on_lot(5, 100)
    #Called error
    
    print(f"Active lots after sleep: {len(b.get_active_lots())}") # Має бути 0
    print("=== BidManager Testing Finished ===")
