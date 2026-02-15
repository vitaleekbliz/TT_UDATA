from fastapi import APIRouter, HTTPException, Depends, status
from app.services.bid_manager.bid_manager import BidManager
from app.services.bid_manager.errors import *
from app.services.lot.errors import *
from app.services.ws_lot_manager.ws_lot_manager import WSLotManager
from app.api.routers.lots.models.models_ws_lot import BidPlacedMessage
from app.core.logger.logger import AppLogger
from app.core.config.config import app_logger_settings, auction_settings
from app.api.routers.lots.models.models_lots_endpoints import LotResponse, BidRequest
from typing import List

lot_endpoint_logger = AppLogger("LOTS_ENDPOINT", "lots_endpoint.log", app_logger_settings.LEVEL).get_instance()
router = APIRouter(prefix="/lots", tags=["Lots"])

# Return managers (Singleton)
async def get_ws_lot_manager() -> WSLotManager:
    return WSLotManager()
async def get_bid_manager() -> BidManager:
    return BidManager()

@router.post("/", response_model=LotResponse, status_code=status.HTTP_201_CREATED)
async def create_lot(manager: BidManager = Depends(get_bid_manager)):
    try:
        lot = await manager.create_lot(
            start_lifeduration=auction_settings.START_LIFE_DURATION,
            lifeduration_on_update=auction_settings.UPDATE_LIFE_DURATION,
            bid_step=auction_settings.MIN_BID_INCREMENT
            )
        
        lot_endpoint_logger.info(f"API: Created lot {lot}")
        return lot
    
    except Exception as e:
        lot_endpoint_logger.error(f"API: Failed to create lot. Error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating lot"
        )


@router.get("/", response_model=List[LotResponse])
async def list_active_lots(manager: BidManager = Depends(get_bid_manager)):
    try:
        return await manager.get_active_lots()
    except Exception as e:
        lot_endpoint_logger.error(f"API: Failed to get active lots. Error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting active lots"
        )

@router.post("/{lot_id}/bids")
async def place_bid(lot_id: int, bid_data: BidRequest, bid_manager: BidManager = Depends(get_bid_manager), ws_lot_manager: WSLotManager = Depends(get_ws_lot_manager)):
    try:
        await bid_manager.bid_on_lot(lot_id, bid_data.amount)

        #TODO add message model to broadcast
        message = BidPlacedMessage(
            lot_id=lot_id,
            bidder=bid_data.name,
            amount=bid_data.amount
        )

        await ws_lot_manager.broadcast_to_lot(lot_id, message)

        return {"message": "Bid placed successfully"}
    except AuctionError as e:
        lot_endpoint_logger.warning(f"API: Failed bid on {lot_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    except BidManagerError as e:
        lot_endpoint_logger.warning(f"API: Failed bid on {lot_id}: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    
    except Exception as e:
        lot_endpoint_logger.warning(f"API: Failed bid on {lot_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))