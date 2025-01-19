NEWS_CATEGORY = '''
보안관제
악성코드
랜섬웨어
다크웹
취약점
해킹
OSINT
DEVSECOPS
OT 보안
IT 보안 
LLM
AI
기타
'''

LANGUAGE_CATEGORY = '''
한국어
영어
기타
'''

SYNONYM_DICTIONARY = { 
    'security operation service': '보안관제',
    'malware': '악성코드',
    'ransomware': '랜섬웨어',
    'darkweb': '다크웹',
    'vulnerability': '취약점',
    '보안 취약점': '취약점',
    'hacking': '해킹',
    'phishing': '피싱',
    'OT security': 'OT 보안',
    '사이버 security': 'IT 보안', 
    'IT security': 'IT 보안',
    'cyber security': 'IT 보안',
    '인공지능 LLM': 'LLM',
    'AI LLM': 'LLM',
    '인공지능': 'AI'
}

CATEGORIES = {'news': NEWS_CATEGORY, 'language': LANGUAGE_CATEGORY}