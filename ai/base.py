import re
import time 
import requests
from configs import logger

class BaseServing():
    def __init__(self):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        self.llm_model = ''
    
    def get_news_summary(self, news_list):
        for news in news_list:
            if news['content']:
                news['summary'] = self.summarize_content(news['content'], news['lang_kor'])
                news['llm_model'] = self.model
                news['content_size'] = len(news['content'])
                news['summary_size'] = len(news['summary'])
                news['compression_ratio'] = round(news['summary_size'] / news['content_size'], 3) 
        return news_list 
    
    def summarize_content(self, content, lang_kor):
        if lang_kor:
            summary = self.summarize_korean_content_with_bare_api(content)
        else:
            summary = self.summarize_english_content_with_bare_api(content)
        return summary

    def summarize_korean_content_with_bare_api(self, text):
        try:
            prompt = '이 문서의 주요 내용을 요약해 주세요. 요약은 간결하게 하되, 문서의 핵심 정보를 포함해야 하며 고유 명사를 제외하고는 한국어로 표시가 되어야 합니다.: {}' \
                '\n\n' \
                '요약:'.format(text)
            result = self.get_result_from_llm(prompt)
            self.logger.info(result)
            self.logger.info('-----')
            result = self.replace_n_to_br(result)
            self.logger.info(result)
            return result
        except Exception as e:
            self.logger.error(e)
            return ''

    def summarize_english_content_with_bare_api(self, text):
        try:
            prompt = 'Without line break and key points, Please summarize the following text into English. the summary must be in English' \
                '\n\n' \
                'Text: {}' \
                '\n\n' \
                'Summary:'.format(text)
            result = self.get_result_from_llm(prompt)
            self.logger.info(result)
            self.logger.info('-----')
            if result:
                prompt = 'Without explanation and line break, translate the following text into Korean. the summary must be in Korean' \
                '\n\n' \
                'Text: {}'.format(result)
                result = self.get_result_from_llm(prompt)
                self.logger.info(result)
                self.logger.info('-----')
                result = self.replace_n_to_br(result)
                self.logger.info(result)
            return result
        except Exception as e:
            logger.error(e)
            return ''

    def get_result_from_llm(self, prompt):
        return ''

    def get_base_result_from_llm(self, url, method='GET', data=[]):
        timestamp = time.time()

        if method == 'GET':
            response = requests.get(url, headers=self.headers)
        else:
            response = requests.post(url, json=data, headers=self.headers)

        # 응답 데이터 처리
        if response.status_code == 200:
            result = response.json()
        else:
            self.logger.error(f'Failed to fetch data: {response.status_code}')
            self.logger.error(response.text)
            result = ''
        self.logger.info(f'LMM resposne_time: {round(time.time() - timestamp, 2)}')
        return result

    def remove_leading_br(self, result):
        # 정규 표현식을 사용하여 맨 앞에 있는 <br> 태그를 제거합니다.
        return re.sub(r'^\s*<br\s*/?>\s*', '', result, flags=re.IGNORECASE)

    def replace_n_to_br(self, result):
        result = result.replace('\n\n', '\n')
        result = self.remove_leading_br(result.replace('\n', '<br>'))
        resilt = re.sub(r'\*\*요약:\*\*<br>', '', result)
        result = re.sub(r'\*\*Summary:\*\*<br>', '', result)
        result = re.sub(r'\*\*', '', result) 
        result = result.replace('요약:<br>', '')
        return result