from fastapi import APIRouter, HTTPException, Depends, status
from app.services.bid_manager.bid_manager import BidManager
from app.core.logger.logger import AppLogger
from app.core.config.config import app_logger_settings, auction_settings
from app.api.routers.lots.models.models_lots_endpoints import LotResponse, BidRequest
from typing import List

lot_endpoint_logger = AppLogger("LOTS_ENDPOINT", "lots_endpoint.log", app_logger_settings.LEVEL).get_instance()
router = APIRouter(prefix="/lots", tags=["Lots"])

# Return manager (Singleton)
def get_manager():
    return BidManager() 

@router.post("/", response_model=LotResponse, status_code=status.HTTP_201_CREATED)
async def create_lot(manager: BidManager = Depends(get_manager)):
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
async def list_active_lots(manager: BidManager = Depends(get_manager)):
    try:
        return await manager.get_active_lots()
    except Exception as e:
        lot_endpoint_logger.error(f"API: Failed to get active lots. Error: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting active lots"
        )

@router.post("/{lot_id}/bids")
async def place_bid(lot_id: int, bid_data: BidRequest, manager: BidManager = Depends(get_manager)):
    try:
        await manager.bid_on_lot(lot_id, bid_data.amount)
        return {"message": "Bid placed successfully"}
    except Exception as e:
        lot_endpoint_logger.warning(f"API: Failed bid on {lot_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))