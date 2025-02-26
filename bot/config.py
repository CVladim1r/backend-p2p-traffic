import os
import logging
import sys

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


BOT_TOKEN = os.getenv('BOT_TOKEN')
BACKEND_API_URL = os.getenv('BACKEND_API_URL')
PASSWORD= os.getenv('PASSWORD')
MINIAPP_URL = os.getenv("MINIAPP_URL")
METRICS_API = os.getenv("BACK_METRICS_API")
