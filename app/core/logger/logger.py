import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

class AppLogger:
    def __init__(self, name: str, log_file: str = "app.log", level = logging.INFO):
        # Створюємо директорію для логів, якщо її немає
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Формат: Час - Канал - Рівень - Повідомлення
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 1. Handler для консолі (важливо для Docker)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 2. Handler для файлу з ротацією
        # (Файл не буде розростатися до нескінченності: max 5MB, зберігаємо 3 останні копії)
        file_handler = RotatingFileHandler(
            log_dir / log_file, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_instance(self):
        return self.logger
