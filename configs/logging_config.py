import os
import logging
from logging.config import dictConfig

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

# Error
ERROR_DIR = 'logs/errors'
if not os.path.exists(ERROR_DIR):
    os.mkdir(ERROR_DIR)

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR + '/project.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})
logger = logging.getLogger(__name__)