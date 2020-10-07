import logging
import logging.config
import sys

logging.getLogger(__name__).addHandler(logging.NullHandler())

def start_logger():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(module)s %(levelname)s:\t%(message)s',
        datefmt='%d.%m.%Y %H:%M:%S')