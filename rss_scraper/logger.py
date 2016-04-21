
import logging


logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)-15s - %(name)s - %(levelname)s: %(message)s',
    datefmt='[%d/%b/%Y %H:%M:%S]'
)

log = logging.getLogger()
