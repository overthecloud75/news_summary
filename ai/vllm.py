
from .base import BaseServing
from configs import LLM_DOMAIN

class VLLM(BaseServing):
    def __init__(self):
        super().__init__()
        self.model, self.max_token = self.get_llm_model()

    def get_llm_model(self):
        llm_url = LLM_DOMAIN + '/v1/models'
        result = self.get_base_result_from_llm(llm_url, method='GET')
        if result and result['data']:
            llm_model = result['data'][0]['id']
            max_token = 128000
        else:
            llm_model = ''
            max_token = 0
        return llm_model, max_token
    
    def get_result_from_llm(self, prompt, messages=[]):
        llm_url = LLM_DOMAIN + '/v1/chat/completions'
        if messages:
            messages.append({'role': 'user', 'content': prompt})
        else:
            messages = [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        result = ''
        if self.model:
            data = {'model': self.model, 'messages': messages, 'temperature': 0.3}
            response_json = self.get_base_result_from_llm(llm_url, method='POST', data=data)
            if response_json:
                try:
                    result = response_json['choices'][0]['message']['content']
                except Exception as e:
                    self.logger.error(e)
        messages.append({'role': 'assistant', 'content': result})
        return result, messages