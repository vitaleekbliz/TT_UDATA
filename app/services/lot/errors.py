class AuctionError(Exception):
    """Base auction error class"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class AuctionEndedError(AuctionError):
    """Bidding on closed lot"""
    def __init__(self, message: str, status_code: int = 404):
        self.message = message
        self.status_code = status_code

class AuctionBidTooLowError(AuctionError):
    """Bidding value is too low to update lot"""
    def __init__(self, message: str, status_code: int = 444):
        self.message = message
        self.status_code = status_code