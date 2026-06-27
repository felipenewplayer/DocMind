import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ------- Configuraçãi básica ------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class BrazilianFormatter(logging.Formatter):
    def formatTime(self, record, datefmt = None):
        dt = datetime.fromtimestamp(
            record.created,
            tz=ZoneInfo("America/Sao_Paulo")
        )
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%d-%m-%Y %H:%M:%S")

formatter = BrazilianFormatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

file_handler = logging.FileHandler(
    LOG_DIR / "app.log",
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        stream_handler,
    ]
)


# Silencia logs verbosos de bibliotecas externas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str):
    return logging.getLogger(name)