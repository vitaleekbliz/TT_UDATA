from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

class AuctionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    START_LIFE_DURATION: int = 30
    UPDATE_LIFE_DURATION: int = 10
    MIN_BID_INCREMENT: int = 10

class AppLoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LOG_", extra="ignore")
    
    FILE_LEVEL: int = logging.DEBUG # Use LOG_FILE_LEVEL
    CONSOLE_LEVEL: int = logging.INFO # Use LOG_CONSOLE_LEVEL

auction_settings = AuctionSettings()
app_logger_settings = AppLoggerSettings()