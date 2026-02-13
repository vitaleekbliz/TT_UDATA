class AuctionError(Exception):
    """Base auction error class"""
    pass

class AuctionEndedError(AuctionError):
    """Bidding on closed lot"""
    pass

class AuctionBidTooLowError(AuctionError):
    """Bidding value is too low to update lot"""
    pass