import requests
import time

from configs import LLM_URL, LLM_MODEL, logger


headers = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json'
}

def summarize_koren_contents_with_bare_api(text):
    try:
        prompt = '이 문서의 주요 내용을 요약해 주세요. 요약은 간결하게 하되, 문서의 핵심 정보를 포함해야 합니다.: {}' \
            '\n\n' \
            'Summary:'.format(text)
        response = get_from_ollama(prompt)
        logger.info(response)
        return response

    except Exception as e:
        logger.error(e)
        return ''

def get_from_ollama(prompt):
    timestamp = time.time()
    data = {'model': LLM_MODEL, 'prompt': prompt, 'stream': False}
    response = requests.post(LLM_URL, json=data, headers=headers)
    logger.info(f"LMM resposne_time: {round(time.time() - timestamp, 2)}")
    # 응답 데이터 처리
    if response.status_code == 200:
        result = response.json()['response']
        return result.replace('\n\n', '\n')
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        logger.error(response.text)
        return ''