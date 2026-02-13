from datetime import datetime, timezone
from app.services.lot.errors import *
from app.services.lot.status import LotStatus

class Lot:
    _static_id_counter = 1
    #TODO create array for bid history

    def __init__(self, starting_price: int = 10, start_lifeduration:int = 30, lifeduration_on_update:int = 10, bid_step:int = 5):
        self.id = self.static_id_couter
        self.static_id_counter+=1

        self.lifeduration = start_lifeduration
        self.lifeduration_on_update = lifeduration_on_update

        self.current_price = starting_price
        self.bid_step = bid_step

        self.start_time = datetime.now(timezone.utc)
        self.end_time = datetime.now(timezone.utc).replace(second=self.timer_start.second + self.lifeduration)

        self.is_closed = False

    def bid(self, new_bid:int):
        if(self.check_status == LotStatus.ENDED):
            raise AuctionEndedError(f"Auction ended at {self.end_time}")
        
        new_price = new_bid + self.bid_step
        if(self.current_price <= new_price):
            raise AuctionBidTooLowError(f"Auction price : {self.current_price}, step : {self.bid_step}; current bid price : {new_price}")

        self._update_price(new_price)

    def _update_price(self, new_val:int):
        self.current_price = new_val

        #update lifetime
        #TODO Ps. very high bid difference (in %) can have short lifetime
        now = datetime.now(timezone.utc)
        self.end_time = now.replace(second=self.now.second + self.lifeduration_on_update)

    def check_status(self) -> LotStatus:
        """Динамічно обчислюємо статус на основі часу"""
        if datetime.now(timezone.utc) >= self.end_time:
            self.is_closed = True
            return LotStatus.ENDED
        
        return LotStatus.RUNNING
