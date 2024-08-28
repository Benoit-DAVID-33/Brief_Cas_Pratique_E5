# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    if not app.debug:
        handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
