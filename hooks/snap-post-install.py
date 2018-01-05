import hooks
import logging
from syncloud_app import logger

logger.init(logging.DEBUG, console=True, line_format='%(message)s')
hooks.install()