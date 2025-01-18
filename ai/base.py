import re
import time 
import requests

from .prompt import SUMMARY_KOREAN_TO_KOREAN, SUMMARY_ENGLISTH_TO_KOREAN, CATEGORY_PROMPT
from configs import logger, SYNONYM_DICTIONARY
from utils import get_yesterday, get_today, is_text_korean_or_english

class BaseServing():
    def __init__(self):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json'
        }
        self.llm_model = ''
    
    def get_news_summary(self, news_list):
        self.logger.info('news summary start!')
        for news in news_list:
            if news['content']:
                text_kor = False
                news['summary'] = self.summarize_content(news['content'], news['lang_kor'])
                news['llm_model'] = self.model
                news['content_size'] = len(news['content'])
                news['summary_size'] = len(news['summary'])
                news['compression_ratio'] = round(news['summary_size'] / news['content_size'], 3) 
        return news_list 

    def get_ti_summary(self, results):
        self.logger.info('ti summary start!')
        ti_results = {
            'ti_indicator': [],
            'ti_description': [],
        }
        yesterday = get_yesterday()
        for result in results:
            created = result['created'].split('.')[0]+'z'
            modified = result['modified'].split('.')[0]+'z'
            indicators = result['indicators']
            if yesterday in modified:
                for indicator in indicators:
                    if result['malware_families']:
                        malware_family = result['malware_families'][0]
                    else:
                        malware_family = ''

                    if result['references']:
                        reference = result['references'][0]
                    else:
                        reference = ''
                    
                    # save indicator 
                    ti_results['ti_indicator'].append({'id': result['id'], 'modified': modified, 'name': result['name'], 'adversary': result['adversary'], 
                        'indicator': indicator['indicator'].replace('.', '[.]'), 'type': indicator['type'], 'malware_family': malware_family})
                summary = self.summarize_content(result['description'], False)
                ti_results['ti_description'].append({'id': result['id'], 'created': created, 'modified': modified, 'name': result['name'], 'description': result['description'], 
                    'summary': summary, 'adversary': result['adversary'], 'malware_family': malware_family, 'reference': reference})
        return ti_results 

    def summarize_content(self, content, lang_kor):
        try:
            if lang_kor:
                prompt = SUMMARY_KOREAN_TO_KOREAN.format(content)
            else:
                prompt = SUMMARY_ENGLISTH_TO_KOREAN.format(content)
            
            text_kor = False
            while not text_kor:
                result = self.get_result_from_llm(prompt)
                self.logger.info('-----')
                result = self.replace_n_to_br(result)
                self.logger.info(result)
                text_kor, korean_ratio = is_text_korean_or_english(result)  # 문장이 한국어인지 판별
                self.logger.info('text_korean_ratio: {}'.format(korean_ratio))
            return result
        except Exception as e:
            self.logger.error(e)
            return ''
        return summary

    def evaluate(self, title, cateogires, news_list):
        self.logger.info('{} llm evaluate start!'.format(title))
        ground_predicted_list = []
        timestamp = get_today() + '_' + str(time.time())[:10]
        for news in news_list:
            ground_predicted = {'title': title, 'timestamp': timestamp}
            if title == 'news': 
                if news['query'] in SYNONYM_DICTIONARY:
                    ground_predicted['ground'] = SYNONYM_DICTIONARY[news['query']]
                else:
                    ground_predicted['ground'] = news['query']
            elif title == 'language':
                if news['lang_kor']:
                    ground_predicted['ground'] = '한국어'
                else: 
                    ground_predicted['ground'] = '영어'
            prompt = CATEGORY_PROMPT.format(cateogires, news['content'])
            ground_predicted['predicted'] = self.get_result_from_llm(prompt)
            ground_predicted['source'] = news['source']
            ground_predicted['name'] = news['name']
            ground_predicted['reference'] = news['reference']
            ground_predicted_list.append(ground_predicted)
            self.logger.info(f'''ground: {ground_predicted['ground']}, 'predicted': {ground_predicted['predicted']} ''')
        return ground_predicted_list
            
    def get_result_from_llm(self, prompt):
        return ''

    def get_base_result_from_llm(self, url, method='GET', data=[]):
        timestamp = time.time()
        try:
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
        except Exception as e:
            self.logger.error(e)
            result = ''
        self.logger.info(f'LMM resposne_time: {round(time.time() - timestamp, 2)}')
        return result

    def remove_leading_br(self, result):
        # 정규 표현식을 사용하여 맨 앞에 있는 <br> 태그를 제거합니다.
        return re.sub(r'^\s*<br\s*/?>\s*', '', result, flags=re.IGNORECASE)

    def replace_n_to_br(self, result):
        result = result.replace('\n\n', '\n')
        result = self.remove_leading_br(result.replace('\n', '<br>'))
        result = re.sub(r'\*\*요약:\*\*<br>', '', result)
        result = re.sub(r'\*\*Summary:\*\*<br>', '', result)
        result = re.sub(r'\*\*', '', result)
        result = result.replace('한국어로 요약된 내용:', '\n')
        result = result.replace('한국어로 요약하자면 다음과 같습니다:', '\n')
        result = result.replace('요약:<br>', '')
        return result