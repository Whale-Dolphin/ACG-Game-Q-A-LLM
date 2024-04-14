import logging

log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_filename = "main.log"

logging.basicConfig(level=logging.INFO, format=log_format, filename=log_filename, filemode='a')

logger = logging.getLogger()