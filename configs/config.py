import os

if os.environ.get('PRODUCTION_MODE'):
    PRODUCTION_MODE = True # Release를 의미 
else:
    PRODUCTION_MODE = False  

LLM_SERVING = 'vllm'

TI_KEYWORD_LIMIT = 5
NEWS_KEYWORD_LIMIT = 3
DELIVERY_HOUR = 9

# TI
NEWS_CATEGORIES = ['보안', 'AI']
NEWS_KEYWORDS = {
    '보안' : {
        '관제': ['악성코드', '랜섬웨어', '다크웹', 'malware', 'ransomware', 'darkweb'],
        '취약점': ['보안 취약점', '해킹', 'vulnerability', 'OSINT', 'hacking'],
        '피싱': ['피싱', 'phishing'],
        'OT 보안' : ['OT 보안', 'OT security'],
        'IT 보안' : ['IT 보안', '사이버 security', 'IT security', 'cyber security'],
    }, 
    'AI' : {
        'AI': ['인공지능 LLM', 'AI LLM'] 
    }
}

RELIABLE_NEWS_SOURCE = {
    '보안' : ['보안뉴스', '디지털타임스', '데일리시큐', '디지털데일리', 'CIO.com', 'Security & Intelligence 이글루코퍼이션', 
                'CybersecurityNews', 'SecurityInfoWatch', 'The Hacker News', 'CSO Online', 'SecurityWeek', 'Security Intelligence', 'Cybersecurity Dive', 'GBHackers'],
    'AI' : ['AI타임스', '인공지능신문', 'Towards Data Science']
} 

# Log
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR ):
    os.mkdir(LOG_DIR )

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)