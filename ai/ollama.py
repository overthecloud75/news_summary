from .base import BaseServing
from configs import LLM_DOMAIN

class Ollama(BaseServing):
    def __init__(self):
        super().__init__()
        self.model = self.get_llm_model()

    def get_llm_model(self):
        llm_url = LLM_DOMAIN + '/api/tags'
        result = self.get_base_result_from_llm(llm_url, method='GET')
        if result and result['models']:
            llm_model = result['models'][0]['name']
        else:
            llm_model = ''
        return llm_model
    
    def get_result_from_llm(self, prompt):
        llm_url = LLM_DOMAIN + '/api/generate'
        if self.model:
            data = {'model': self.model, 'prompt': prompt, 'stream': False}
            result = self.get_base_result_from_llm(llm_url, method='POST', data=data)
            if result:
                try:
                    result = result['response']
                except Exception as e:
                    self.logger.error(e)
                    result = ''
        else:
            result = ''
        return result 
