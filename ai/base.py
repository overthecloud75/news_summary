import time
import requests

from .prompt import *
from configs import logger, SYNONYM_DICTIONARY, LLM_API_KEY
from utils import is_text_korean_or_english, strip_useless

class BaseServing():
    def __init__(self):
        self.logger = logger
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LLM_API_KEY}' 
        }

    def summarize_content(self, content, lang_kor):
        try:
            prompt = self.make_summary_prompt(content, lang_kor)
            token_len = self.get_token_length(prompt, lang_kor)
            if token_len < self.max_token:
                text_kor = False
                while not text_kor:
                    result, _ = self.get_result_from_llm(prompt)
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
            self.logger.info(content)
            prompt = self.make_deep_prompt(content, lang_kor, category=category)
            token_len = self.get_token_length(prompt, lang_kor)
            if token_len < self.max_token:
                text_kor = False
                while not text_kor:
                    result, _ = self.get_result_from_llm(prompt)
                    self.logger.info('-----')
                    self.logger.info(result)
                    text_kor, korean_ratio = is_text_korean_or_english(result)  # 문장이 한국어인지 판별
                    self.logger.info('text_korean_ratio: {}'.format(korean_ratio))
                    if not text_kor:
                        prompt = self.make_deep_prompt(content, lang_kor, category=category)
                result = self.revise_report(result)  # 보고서를 개선 
                return result
            else:
                content = content[:int(len(content) * 0.9)]
                return self.deep_research(content, lang_kor)
        except Exception as e:
            self.logger.error(e)
            return ''
    
    def revise_report(self, report):
        prompt = REVISED_REPORT_PROMPT.format(report)
        result, _ = self.get_result_from_llm(prompt)
        self.logger.info('-----')
        self.logger.info(result)
        return result 

    def evaluate_report(self, news):
        prompt = CATEGORY_REPORT_PROMPT.format(news['content'])
        result, _ = self.get_result_from_llm(prompt)
        return result

    def category_predict(self, categories, title, news, evaluation_type='zero shot'):
        if evaluation_type == 'few shot':
            prompt = CATEGORY_FEW_PROMPT.format(categories, news['content'])
        elif evaluation_type == 'few shot json':
            prompt = CATEGORY_FEW_JSON_PROMPT.format(categories, news['content'])
        else:
            prompt = CATEGORY_PROMPT.format(categories, news['content'])
        predicted, _ = self.get_result_from_llm(prompt)
        return predicted 
            
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

