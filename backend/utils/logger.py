# backend/utils/logger.py

from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time}</green> | <level>{message}</level>", level="INFO")

__all__ = ["logger"]