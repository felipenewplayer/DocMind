import logging
from pathlib import Path

# ------- Configuraçãi básica ------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log" , encoding="utf-8"),
        logging.StreamHandler(),
    ]
)


# Silencia logs verbosos de bibliotecas externas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str):
    return logging.getLogger(name)