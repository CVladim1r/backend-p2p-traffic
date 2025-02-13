import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

BOT_HELPER_TOKEN = os.getenv("BOT_HELPER_TOKEN")
USER_HELPER_ID = int(os.getenv("USER_HELPER_ID")) if os.getenv("USER_HELPER_ID") else None