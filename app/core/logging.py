import logging
import sys

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
