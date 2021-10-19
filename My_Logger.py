import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter("[%(levelname)s][%(asctime)s]:%(funcName)s - %(message)s")

logFile = "./dmhy-watcher.log"

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                backupCount=1, encoding="utf-8")
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

logger.addHandler(my_handler)


def broadcastCriticalMsg(msg:str) -> None:
    print(msg)
    logger.critical(msg)

def broadcastErrorMsg(msg:str) -> None:
    print(msg)
    logger.error(msg)

def broadcastWarningMsg(msg:str) -> None:
    print(msg)
    logger.warning(msg)

def broadcastInfoMsg(msg:str) -> None:
    print(msg)
    logger.info(msg)

def broadcastDebugMsg(msg:str) -> None:
    print(msg)
    logger.debug(msg)
