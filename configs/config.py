import os

if os.environ.get('PRODUCTION_MODE'):
    PRODUCTION_MODE = True # Release를 의미 
else:
    PRODUCTION_MODE = False  

KEYWORD_NEWS_LIMIT = 2
DELIVERY_HOUR = 9

# TI
TI_NAME = 'Google News'
NEWS_KEYWORD_LIST = ['보안', 'IT 보안', 'cyber security', '인공지능 LLM']
RELIABLE_NEWS_SOURCE = ['보안뉴스', '디지털타임스', '데일리시큐', 'CIO.com', 'CybersecurityNews', 'SecurityInfoWatch', 'The Hacker News', 'AI타임스'] 
   # 'CyberNews.com', 'The Hacker News'
   # 'Cybersecurity Dive', 'Security Intelligence', 'SecuringIndustry.com', 'SecurityWeek', 'Intelligent CISO'

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)