
from .base import BaseServing
from configs import LLM_DOMAIN

class VLLM(BaseServing):
    def __init__(self):
        super().__init__()
        self.model = self.get_llm_model()

    def get_llm_model(self):
        llm_url = LLM_DOMAIN + '/v1/models'
        result = self.get_base_result_from_llm(llm_url, method='GET')
        if result and result['data']:
            llm_model = result['data'][0]['id']
        else:
            llm_model = ''
        return llm_model
    
    def get_result_from_llm(self, prompt):
        llm_url = LLM_DOMAIN + '/v1/chat/completions'
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ]
        if self.model:
            data = {'model': self.model, 'messages': messages, 'temperature': 0.7}
            result = self.get_base_result_from_llm(llm_url, method='POST', data=data)
            if result:
                try:
                    result = result['choices'][0]['message']['content']
                except Exception as e:
                    self.logger.error(e)
                    result = ''
        else:
            result = ''
        return result 