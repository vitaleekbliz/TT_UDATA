class AuctionError(Exception):
    """Базовий клас для помилок аукціону"""
    pass

class AuctionEndedError(AuctionError):
    """Виникає, коли ставка ставиться на закритий лот"""
    pass

class AuctionBidTooLowError(AuctionError):
    """Виникає, коли ставка ставиться на закритий лот"""
    pass