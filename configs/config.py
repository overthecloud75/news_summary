import os

if os.environ.get('PRODUCTION_MODE'):
    PRODUCTION_MODE = True # Release를 의미 
else:
    PRODUCTION_MODE = False  

if os.environ.get('SEND_EMAIL'):
    SEND_EMAIL = True 
else:
    SEND_EMAIL = True

LLM_SERVING = 'vllm'

TI_KEYWORD_LIMIT = 4
NEWS_KEYWORD_LIMIT = 2
DEEP_RESEARCH_MINIMUM_SCORE = 90
DELIVERY_HOUR = 9

# TI
NEWS_CATEGORIES = ['보안', 'AI']
NEWS_KEYWORDS = {
    '보안' : {
        '관제': ['보안관제', '악성코드', '랜섬웨어', '다크웹', 'security operation service', 'malware', 'ransomware', 'darkweb'],
        '취약점': ['보안 취약점', '해킹', 'vulnerability', 'OSINT', 'hacking'],
        '피싱': ['피싱', 'phishing'],
        'DEVSECOPS': ['DEVSECOPS'],
        'OT 보안' : ['OT 보안', 'OT security'],
        'IT 보안' : ['IT 보안', '사이버 security', 'IT security', 'cyber security'],
    },
    'AI' : {
        'AI': ['인공지능 LLM', 'AI LLM', '인공지능', 'AI ROBOT'] 
    }
}

RELIABLE_NEWS_SOURCE = {
    '보안' : ['보안뉴스', '디지털타임스', '데일리시큐', '디지털데일리', 'CIO.com', 'Security & Intelligence 이글루코퍼이션',
                'CybersecurityNews', 'SecurityInfoWatch', 'The Hacker News', 'CSO Online', 'SecurityWeek', 'Security Intelligence', 'Cybersecurity Dive', 'GBHackers', 'DevOps.com', 
                'MSSP Alert', 'The Record from Recorded Future News', 'Darktrace'],
    'AI' : ['AI타임스', '인공지능신문', 'MIT 테크놀로지 리뷰', '더에이아이(THE AI)', 'Towards Data Science', 'Google DeepMind', 'insideAI News']
} 

TRAF_EXCEPTION_NEWS_SOURCE = ['보안뉴스', '디지털데일리', 'The Hacker News', 'SecurityWeek']

# csv
CSV_DIR = 'csv'
if not os.path.exists(CSV_DIR):
    os.mkdir(CSV_DIR)