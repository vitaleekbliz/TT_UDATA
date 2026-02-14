from pydantic import BaseModel

class BidPlacedMessage(BaseModel):
    type: str = "bid_placed"
    lot_id: int
    bidder: str
    amount: int