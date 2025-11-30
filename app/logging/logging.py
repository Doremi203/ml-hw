from loguru import logger
import sys
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time}</green> | {level} | {message}")
logger.add(LOGS_DIR / "service.log", level="INFO", rotation="10 MB", retention="10 days")

__all__ = ["logger"]