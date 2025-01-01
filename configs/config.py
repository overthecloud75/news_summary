import os

PRODUCTION_MODE = False  # Release를 의미 

RELIABLE_NEWS_SOURCE = ['보안뉴스', '디지털타임스']

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)