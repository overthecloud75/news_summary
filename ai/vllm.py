
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
        if not messages:
            messages = [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        else:
            messages.append({'role': 'ueer', 'content': prompt})
        if self.model:
            data = {'model': self.model, 'messages': messages, 'temperature': 0.3}
            result = self.get_base_result_from_llm(llm_url, method='POST', data=data)
            if result:
                try:
                    result = result['choices'][0]['message']['content']
                except Exception as e:
                    self.logger.error(e)
                    result = ''
        else:
            result = ''
        messages.append({'role': 'assistant', 'content': result})
        return result, messages