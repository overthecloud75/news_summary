import os

if os.environ.get('PRODUCTION_MODE'):
    PRODUCTION_MODE = True # Release를 의미 
else:
    PRODUCTION_MODE = False  

LLM_SERVING = 'vllm'

KEYWORD_NEWS_LIMIT = 4
DELIVERY_HOUR = 10

# TI
TI_NAME = 'Google News'
NEWS_KEYWORD_LIST = ['보안', 'IT 보안', '사이버 security', 'IT security', 'cyber security', '인공지능 LLM', 'AI LLM']
RELIABLE_NEWS_SOURCE = ['보안뉴스', '디지털타임스', '데일리시큐', '디지털데일리', 'CIO.com', 'Security & Intelligence 이글루코퍼이션', 
    'CybersecurityNews', 'SecurityInfoWatch', 'The Hacker News', 'CSO Online', 'SecurityWeek', 'Security Intelligence', 'Cybersecurity Dive', 
    'AI타임스', '인공지능신문', 'Towards Data Science'] 
   # 'CyberNews.com'

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)