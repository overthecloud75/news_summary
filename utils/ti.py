from datetime import datetime, timedelta
import requests

from configs import PRODUCTION_MODE, TI_KEYWORD_LIMIT, TI_API_KEY, TI_API_URL, logger

# 헤더에 API 키 포함
headers = {
    'X-OTX-API-KEY': TI_API_KEY,
    'Content-Type': 'application/json'
}

def get_results_from_ti():
    results = []
    modified_since = (datetime.utcnow() - timedelta(hours=48)).isoformat() + 'Z'
    params = {
        'modified_since': modified_since,
        'limit': 1000
    }
    # GET 요청 보내기
    response = requests.get(TI_API_URL, headers=headers, params=params)

    # 응답 데이터 처리
    if response.status_code == 200:
        pulses = response.json()
        results = pulses['results']
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        logger.error(response.text)

    if PRODUCTION_MODE:
        return results
    else:
        return results[:TI_KEYWORD_LIMIT]