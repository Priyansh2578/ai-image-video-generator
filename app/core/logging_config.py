import logging
import sys
from loguru import logger
from .config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logger.add(
        settings.LOG_FILE,
        rotation="500 MB",
        retention="10 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    logger.add(
        settings.ERROR_LOG_FILE,
        rotation="500 MB",
        retention="30 days",
        level="ERROR"
    )
    logger.add(sys.stdout, level=settings.LOG_LEVEL)
