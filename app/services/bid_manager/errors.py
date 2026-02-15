class BidManagerError(Exception):
    """Base error class bid manager"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class BidManagerLotIsNotFoundError(BidManagerError):
    """Lot is not found in the dictionary"""
    def __init__(self, message: str, status_code: int = 404):
        self.message = message
        self.status_code = status_code