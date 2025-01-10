import os
import logging
import sys

from dotenv import load_dotenv

load_dotenv()


def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


BOT_TOKEN = os.getenv('BOT_TOKEN')
BACKEND_API_URL = os.getenv('BACKEND_API_URL')
PASSWORD= os.getenv('PASSWORD')
MINIAPP_URL = os.getenv("MINIAPP_URL")
METRICS_API = os.getenv("BACK_METRICS_API", "http://localhost:8000/metrics")


db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT")
db_host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB")
db_url = f"postgres://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
