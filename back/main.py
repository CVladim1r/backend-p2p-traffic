import logging
import uvicorn

from back.config import debug

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"


if __name__ == "__main__":
    logging.info("Application GATEWAY RUN ")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=9100,
        reload=debug,
        workers=1,
        log_config=log_config,
        reload_dirs=["./"],
    )

