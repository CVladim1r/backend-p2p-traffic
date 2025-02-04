import os

from dotenv import load_dotenv

load_dotenv()


CRYPTBOT_WEBHOOK_URL = os.getenv("CRYPTBOT_WEBHOOK_URL")
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
IS_TESTNET = os.getenv("IS_TESTNET")
SECRET_KEY_DEALS = os.getenv("SECRET_KEY_DEALS")

debug = os.getenv("DEBUG")

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["back.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}