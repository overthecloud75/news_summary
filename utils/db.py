import requests

from configs import NEWS_SAVE_URL, NEWS_SAVE_API_KEY, logger

def save_news_to_db(result):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    } 
    response = requests.post(NEWS_SAVE_URL + '?api_key=' + NEWS_SAVE_API_KEY, json=result, headers=headers)
    # 응답 데이터 처리
    if response.status_code == 200:
        pass 
    else:
        logger.error(f'Failed to fetch data: {response.status_code}')
        logger.error(response.text)


   