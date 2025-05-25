import requests

from configs import API_KEY, logger

def save_to_db(url, results):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    } 
    response = requests.post(url + '?api_key=' + API_KEY, json=results, headers=headers)
    # 응답 데이터 처리
    if response.status_code == 200:
        pass 
    else:
        logger.info(f'''url: {url}''')
        logger.error(f'Failed to fetch data: {response.status_code}')
        logger.error(response.text)



   