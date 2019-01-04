import logging


logger = logging.getLogger(__name__)

formatter = logging.Formatter(
    '[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)
