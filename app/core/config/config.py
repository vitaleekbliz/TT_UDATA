from pydantic_settings import BaseSettings
import logging

class AuctionSettings(BaseSettings):
    START_LIFE_DURATION: int = 3
    UPDATE_LIFE_DURATION: int = 3
    MIN_BID_INCREMENT: int = 10

class AppLoggerSettings(BaseSettings):
    LEVEL: int = logging.DEBUG

auction_settings = AuctionSettings()
app_logger_settings = AppLoggerSettings()