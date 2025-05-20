import re
import time 
import requests

from .prompt import *
from configs import logger, SYNONYM_DICTIONARY, LLM_API_KEY
from utils import get_yesterday, get_today, is_text_korean_or_english, strip_useless

class BaseServing():
    def __init__(self):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LLM_API_KEY}' 
        }
    
    def get_news_summary(self, news_list):
        self.logger.info('news summary start!')
        for news in news_list:
            if news['content']:
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
            if result['malware_families']:
                malware_family = result['malware_families'][0]
            else:
                malware_family = ''
            if result['references']:
                reference = result['references'][0]
            else:
                reference = ''
            if yesterday in modified:
                for indicator in indicators:        
                    # save indicator 
                    ti_results['ti_indicator'].append({'id': result['id'], 'modified': modified, 'name': result['name'], 'adversary': result['adversary'], 
                        'indicator': indicator['indicator'].replace('.', '[.]'), 'type': indicator['type'], 'malware_family': malware_family})
                summary = self.summarize_content(result['description'], False)
                ti_results['ti_description'].append({'id': result['id'], 'created': created, 'modified': modified, 'name': result['name'], 'description': result['description'], 
                    'summary': summary, 'adversary': result['adversary'], 'malware_family': malware_family, 'reference': reference})
        return ti_results 

    def summarize_content(self, content, lang_kor):
        try:
            prompt = self.make_summary_prompt(content, lang_kor)
            token_len = self.get_token_length(prompt, lang_kor)
            if token_len < self.max_token:
                text_kor = False
                summary_count = 0 
                while not text_kor:
                    result, messages = self.get_result_from_llm(prompt)
                    self.logger.info('-----')
                    result = strip_useless(result)
                    self.logger.info(result)
                    text_kor, korean_ratio = is_text_korean_or_english(result)  # 문장이 한국어인지 판별
                    self.logger.info('text_korean_ratio: {}'.format(korean_ratio))
                    if not text_kor:
                        prompt = self.make_summary_prompt(result, lang_kor)
                return result
            else:
                content = content[:int(len(content) * 0.9)]
                return self.summarize_content(content, lang_kor)
        except Exception as e:
            self.logger.error(e)
            return ''
    
    def deep_research(self, news):
        try:
            content = news['content']
            lang_kor = news['lang_kor']
            category = news['category']
            prompt = self.make_deep_prompt(content, lang_kor, category=category)
            token_len = self.get_token_length(prompt, lang_kor)
            if token_len < self.max_token:
                text_kor = False
                report_count = 0 
                while not text_kor:
                    result, messages = self.get_result_from_llm(prompt)
                    self.logger.info('-----')
                    self.logger.info(result)
                    text_kor, korean_ratio = is_text_korean_or_english(result)  # 문장이 한국어인지 판별
                    self.logger.info('text_korean_ratio: {}'.format(korean_ratio))
                    if not text_kor:
                        prompt = self.make_deep_prompt(content, lang_kor)
                return result
            else:
                content = content[:int(len(content) * 0.9)]
                return self.deep_research(content, lang_kor)
        except Exception as e:
            self.logger.error(e)
            return ''

    def evaluate(self, title, cateogires, news_list, evaluation_type='zero shot'):
        self.logger.info(f'''{title} {evaluation_type} llm evaluate start!''')
        ground_predicted_list = []
        timestamp = get_today() + '_' + str(time.time())[:10]
        for news in news_list:
            try:
                if evaluation_type == 'few shot':
                    prompt = CATEGORY_FEW_PROMPT.format(cateogires, news['content'])
                elif evaluation_type == 'few shot json':
                    prompt = CATEGORY_FEW_JSON_PROMPT.format(cateogires, news['content'])
                else:
                    prompt = CATEGORY_PROMPT.format(cateogires, news['content'])
                predicted = self.category_predict(title, timestamp, prompt, news)
                ground_predicted_list.append(predicted)
            except Exception as e:
                self.logger.error(e)
        return ground_predicted_list

    def evaluate_reports(self, news_list):
        self.logger.info(f'''llm evaluate report start!''')
        ground_predicted_list = []
        for news in news_list:
            try:
                prompt = CATEGORY_REPORT_PROMPT.format(news['content'])
                result, messages = self.get_result_from_llm(prompt)
                self.logger.info('report 설명: {}'.format(result))
                score = self.get_point_from_result(result)
                ground_predicted_list.append(score)
            except Exception as e:
                self.logger.error(e)
        return ground_predicted_list

    def get_point_from_result(self, result):
        pattern = r'(총점|점수|평가|결과):\*?\*?\s*(\d+)\s*(?:/|\점|점)?\s*(?:\d+)?'
        match = re.search(pattern, result)
        try:
            if match:
                score = int(match.group(2))
                self.logger.info('score: {}'.format(score))
                if score <= 100:
                    return score
                else:
                    return 0 
            else:
                self.logger.error('score를 찾을 수 없습니다.')
                return 0
        except Exception as e:
            self.logger.error(e)
            return 0 

    def category_predict(self, title, timestamp, prompt, news):
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
        ground_predicted['predicted'] = self.get_result_from_llm(prompt)
        ground_predicted['source'] = news['source']
        ground_predicted['name'] = news['name']
        ground_predicted['reference'] = news['reference']
        self.logger.info(f'''ground: {ground_predicted['ground']}, 'predicted': {ground_predicted['predicted']}''')
        return ground_predicted
            
    def get_result_from_llm(self, prompt, messages=[]):
        return '', []

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

    def make_summary_prompt(self, content, lang_kor):
        if lang_kor:
            prompt = SUMMARY_KOREAN_TO_KOREAN.format(content)
        else:
            prompt = SUMMARY_ENGLISTH_TO_KOREAN.format(content)
        return prompt

    def make_deep_prompt(self, content, lang_kor, category='보안'):
        if category == '보안':
            if lang_kor:
                prompt = SECURITY_REPORT_KOREAN_TO_KOREAN.format(content)
            else:
                prompt = SECURITY_REPORT_ENGLISH_TO_KOREAN.format(content)
        else:
            if lang_kor:
                prompt = REPORT_KOREAN_TO_KOREAN.format(content)
            else:
                prompt = SECURITY_ENGLISH_TO_KOREAN.format(content)
        return prompt

    def get_token_length(self, prompt, lang_kor):
        '''
            영어: 토큰 개수 ≈ 단어 개수 * 1.3
            한국어/중국어/일본어: 토큰 개수 ≈ 글자 개수 * 2
            혼합 텍스트 (한/영/숫자 포함): 토큰 개수 ≈ 글자 개수 * 1.5  
        '''
        if lang_kor:
            token_len = len(prompt.split(' ')) * 2
        else:
            token_len = len(prompt.split(' ')) * 1.3 
        return token_len

