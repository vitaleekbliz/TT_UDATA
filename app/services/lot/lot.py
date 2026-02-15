from datetime import datetime, timedelta
from app.services.lot.errors import *
from app.services.lot.status import LotStatus
from app.core.logger.logger import AppLogger
from app.core.config.config import app_logger_settings
from app.api.routers.lots.models.models_lots_endpoints import LotResponse

class Lot:
    _id_counter = 1
    _auction_logger = AppLogger("AUCTION", "auction.log", app_logger_settings.FILE_LEVEL).get_instance()
    #TODO create array for bid history

    def __init__(self, starting_price: int = 10, start_lifeduration:int = 5, lifeduration_on_update:int = 5, bid_step:int = 5):

        self._id = self._id_counter
        Lot._id_counter+=1

        self._auction_logger.info(f"created new lot id={self._id} ")

        self._lifeduration = start_lifeduration
        self._lifeduration_on_update = lifeduration_on_update

        self._current_price = starting_price
        self._bid_step = bid_step

        self._start_time = datetime.now()
        self._end_time = self._start_time + timedelta(seconds=self._lifeduration)

        self._is_closed = False

        self._auction_logger.debug(
            f"NEW_LOT: ID={self._id} | "
            f"StartPrice={self._current_price} | "
            f"BidStep={self._bid_step} | "
            f"InitDuration={self._lifeduration}s | "
            f"UpdateBonus={self._lifeduration_on_update}s | "
            f"Start={self._start_time.strftime('%H:%M:%S')} | "
            f"End={self._end_time.strftime('%H:%M:%S')} UTC"
        )


    def get_id(self) -> int:
        return self._id
    
    def get_lot_response_model(self) -> LotResponse:
        """Returns LotResponse for API response => response model"""
        return LotResponse(
            id=self._id,
            current_price=self._current_price, 
            is_open="Open" if not self._is_closed else "Closed",
            start_time=self._start_time,
            end_time=self._end_time
            )
    
    def place_bid(self, new_bid:int):
        """
        Place bid by user
        """
        self._auction_logger.info(f"Trying to bid : {new_bid}")
        if(self.check_status() != LotStatus.RUNNING):
            self._auction_logger.error(f"Lot {self._id} is closed at {self._end_time}")
            raise AuctionEndedError(f"Auction ended at {self._end_time}")
        
        if(new_bid < self._current_price + self._bid_step):
            self._auction_logger.error(f"Bid {new_bid} is too low lot id = {self._id}, price = {self._current_price}, step = {self._bid_step}")
            raise AuctionBidTooLowError(f"Auction price : {self._current_price}, step : {self._bid_step}; current bid price : {new_bid}")

        self._update_price(new_bid)

    def _update_price(self, new_val:int):
        """
        Private function. Should do checks before running the funcion.
        """
        self._auction_logger.info(f"Updated price of {self._id} lot. Old price : {self._current_price }, new = {new_val}")
        self._current_price = new_val

        #update lifetime
        #TODO fix if this behavior is not intended
        # currently placing bed makes lot lifetime shorter, equal to update_lifeduration even if its higher then 
        # Lot lifetime = 30 (start_lifedur) -> place bet -> lifetime drops to 10 (_lifeduration_on_update)
        #Ps. Good for this TT testing; 
        now = datetime.now()
        self._end_time = now + timedelta(seconds=self._lifeduration_on_update)

        self._auction_logger.debug(f"New end time : {self._end_time}")

    def check_status(self) -> LotStatus:
        """Calculate status and close lot is ran out of time"""
        self._auction_logger.debug(f"Checking lot id={self._id}, end time={self._end_time}")

        if self._is_closed or datetime.now() >= self._end_time:
            self._auction_logger.info(f"Updated lot {self._id} to be closed")
            self._is_closed = True
            return LotStatus.ENDED
        
        return LotStatus.RUNNING