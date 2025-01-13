import os

if os.environ.get('PRODUCTION_MODE'):
    PRODUCTION_MODE = True # Release를 의미 
else:
    PRODUCTION_MODE = False  

LLM_SERVING = 'vllm'

KEYWORD_NEWS_LIMIT = 5
DELIVERY_HOUR = 10

# TI
TI_NAME = 'Google News'
NEWS_KEYWORDS = {
    '관제': ['악성코드', '랜섬웨어', '다크웹', 'malware', 'ransomware', 'darkweb'],
    '취약점': ['보안 취약점', '해킹', 'vulnerability', 'OSINT', 'hacking'],
    '피싱': ['피싱', 'phishing'],
    'IT 보안' : ['IT 보안', 'IT 보안', '사이버 security', 'IT security', 'cyber security'],
    'AI': ['인공지능 LLM', 'AI LLM'] 
}

RELIABLE_NEWS_SOURCE = ['보안뉴스', '디지털타임스', '데일리시큐', '디지털데일리', 'CIO.com', 'Security & Intelligence 이글루코퍼이션', 
    'CybersecurityNews', 'SecurityInfoWatch', 'The Hacker News', 'CSO Online', 'SecurityWeek', 'Security Intelligence', 'Cybersecurity Dive', 'GBHackers',
    'AI타임스', '인공지능신문', 'Towards Data Science'] 

RELIABLE_NEWS_SOURCE = ['GBHackers'] 

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)