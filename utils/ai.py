import requests
import time
import re

from configs import LLM_URL, LLM_MODEL, logger


headers = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json'
}

def summarize_korean_content_with_bare_api(text):
    try:
        prompt = '이 문서의 주요 내용을 요약해 주세요. 요약은 간결하게 하되, 문서의 핵심 정보를 포함해야 합니다.: {}' \
            '\n\n' \
            'Summary:'.format(text)
        result = get_from_ollama(prompt)
        logger.info(result)
        logger.info('-----')
        result = replace_n_to_br(result)
        logger.info(result)
        return result

    except Exception as e:
        logger.error(e)
        return ''

def summarize_english_content_with_bare_api(text):
    try:
        prompt = 'Without line break and key points, Please summarize the following text: {}' \
            '\n\n' \
            'Summary:'.format(text)
        result = get_from_ollama(prompt)
        if result:
            prompt = 'Without explanation and line break, translate the following text into Korean: {}'.format(result)
            result = get_from_ollama(prompt)
            logger.info(result)
            logger.info('-----')
            result = replace_n_to_br(result)
            logger.info(result)
        return result

    except Exception as e:
        logger.error(e)
        return ''

def get_from_ollama(prompt):
    timestamp = time.time()
    data = {'model': LLM_MODEL, 'prompt': prompt, 'stream': False}
    response = requests.post(LLM_URL, json=data, headers=headers)
    logger.info(f'LMM resposne_time: {round(time.time() - timestamp, 2)}')
    # 응답 데이터 처리
    if response.status_code == 200:
        result = response.json()['response']
        return result
    else:
        logger.error(f'Failed to fetch data: {response.status_code}')
        logger.error(response.text)
        return ''

def remove_leading_br(result):
    # 정규 표현식을 사용하여 맨 앞에 있는 <br> 태그를 제거합니다.
    return re.sub(r'^\s*<br\s*/?>\s*', '', result, flags=re.IGNORECASE)

def replace_n_to_br(result):
    result = result.replace('\n\n', '\n')
    result = remove_leading_br(result.replace('\n', '<br>'))
    resilt = re.sub(r'\*\*요약:\*\*<br>', '', result)
    result = re.sub(r'\*\*Summary:\*\*<br>', '', result)
    result = re.sub(r'\*\*', '', result) 
    result = result.replace('요약:<br>', '')
    return result

