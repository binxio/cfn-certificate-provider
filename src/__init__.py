from boto3 import set_stream_logger
from os import getenv
from logging import basicConfig, getLogger

logger = getLogger()
logger.setLevel(getenv("LOG_LEVEL", "INFO"))
set_stream_logger("boto3.resources", logger.getEffectiveLevel())
