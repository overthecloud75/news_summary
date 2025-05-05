from .base import BaseServing
from configs import LLM_DOMAIN

class Ollama(BaseServing):
    def __init__(self):
        super().__init__()
        self.model, self.max_token = self.get_llm_model()

    def get_llm_model(self):
        llm_url = LLM_DOMAIN + '/api/tags'
        result = self.get_base_result_from_llm(llm_url, method='GET')
        if result and result['models']:
            llm_model = result['models'][0]['name']
            llm_url = LLM_DOMAIN + 'api/show'
            result = self.get_base_result_from_llm(llm_url, method='POST', data={'model': llm_model})
            architechture = result['model_info']['general.architecture']
            max_token = result['model_info'][architecture+'.'+'context_length']
        else:
            llm_model = ''
            max_token = 0 
        return llm_model, max_token
    
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
