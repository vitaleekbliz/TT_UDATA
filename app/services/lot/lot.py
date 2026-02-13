from datetime import datetime, timezone
from app.services.lot.errors import *
from app.services.lot.status import LotStatus

class Lot:
    _static_id_counter = 1
    #TODO create array for bid history

    def __init__(self, starting_price: int = 10, start_lifeduration:int = 30, lifeduration_on_update:int = 10, bid_step:int = 5):
        self.id = self.static_id_couter
        self.static_id_counter+=1

        self._lifeduration = start_lifeduration
        self._lifeduration_on_update = lifeduration_on_update

        self._current_price = starting_price
        self._bid_step = bid_step

        self._start_time = datetime.now(timezone.utc)
        self._end_time = datetime.now(timezone.utc).replace(second=self.timer_start.second + self._lifeduration)

        self.is_closed = False

    def bid(self, new_bid:int):
        """
        Place bid by user
        """
        if(self.check_status == LotStatus.ENDED):
            raise AuctionEndedError(f"Auction ended at {self._end_time}")
        
        new_price = new_bid + self._bid_step
        if(self._current_price <= new_price):
            raise AuctionBidTooLowError(f"Auction price : {self._current_price}, step : {self._bid_step}; current bid price : {new_price}")

        self._update_price(new_price)

    def _update_price(self, new_val:int):
        """
        Private function. Should do checks before running the funcion.
        """
        self._current_price = new_val

        #update lifetime
        #TODO Ps. very high bid difference (in %) can have short lifetime
        now = datetime.now(timezone.utc)
        self._end_time = now.replace(second=self.now.second + self._lifeduration_on_update)

    def check_status(self) -> LotStatus:
        """Calculate status and close lot is ran out of time"""
        if self.is_closed or datetime.now(timezone.utc) >= self._end_time:
            self.is_closed = True
            return LotStatus.ENDED
        
        return LotStatus.RUNNING

