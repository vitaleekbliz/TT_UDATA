import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config.config import app_logger_settings

class AppLogger:
    def __init__(self, name: str, log_file: str = "app.log", level = app_logger_settings.FILE_LEVEL):
        # Create dir for files
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        #Additional safety net for server reloads
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 1. Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(app_logger_settings.CONSOLE_LEVEL)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 2. File
        file_handler = RotatingFileHandler(
            log_dir / log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setLevel(app_logger_settings.FILE_LEVEL) 
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_instance(self):
        return self.logger
