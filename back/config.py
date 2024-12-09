import os

from dotenv import load_dotenv

load_dotenv()

debug = os.getenv("DEBUG", False)

db_user = os.getenv("POSTGRES_USER", "postgres")
db_pass = os.getenv("POSTGRES_PASSWORD", "q1q1q1q1")
db_port = os.getenv("POSTGRES_PORT", "5432")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_name = os.getenv("POSTGRES_DB", "metrics_db")
db_url = f"postgres://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

TORTOISE_ORM = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": ["back.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}
