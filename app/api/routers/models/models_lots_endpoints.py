from pydantic import BaseModel
from datetime import datetime
from typing import List

class LotResponse(BaseModel):
    id: int
    current_price: int
    status: str
    start_time: datetime
    end_time: datetime

class BidRequest(BaseModel):
    amount: int
    name: str