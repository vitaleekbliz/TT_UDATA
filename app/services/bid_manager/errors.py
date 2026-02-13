class BidManagerError(Exception):
    """Base error class bid manager"""
    pass


class BidManagerLotIsNotFoundError(BidManagerError):
    """Lot is not found in the dictionary"""
    pass