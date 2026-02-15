from pydantic import BaseModel
from datetime import datetime

class LotResponse(BaseModel):
    id: int
    current_price: int
    is_open: str
    start_time: datetime
    end_time: datetime

class BidRequest(BaseModel):
    amount: int
    name: str