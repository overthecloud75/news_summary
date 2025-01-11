import os
import time
import sys

from configs import LLM_SERVING, DELIVERY_HOUR, CSV_DIR, NEWS_BASE, SUBJECT_BASE, logger
from ai import Ollama, VLLM
from utils import read_webdriver, get_cve_data, get_today, get_hour, make_csv_file, get_news_html, send_email

if __name__ == '__main__':
    logger.info('start')
    while True:
        today = get_today()
        hour = get_hour()
        news_file_path = f'{CSV_DIR}/{NEWS_BASE}_{today}.csv'
        subject = f'{SUBJECT_BASE} {today}'

        if LLM_SERVING == 'ollama':
            llm = Ollama()
        elif LLM_SERVING == 'vllm':
            llm = VLLM()
        else:
            logger.error('There is no proper LLM_SERVING.')
            sys.exit()

        if not os.path.exists(news_file_path) and hour >= DELIVERY_HOUR:
            try:
                news_list = read_webdriver()
                news_list = llm.get_news_summary(news_list)
            except Exception as e:
                logger.error(e)
                news_list = []
            if news_list:
                make_csv_file(results=news_list, filename=news_file_path)
                news_html = get_news_html(subject, results=news_list, llm_model=llm.model)
                send_email(news_html, subject=subject)
                #send_email(news_html, subject=subject, attached_file=news_file_path)
        # cve_list = get_cve_data()
        time.sleep(3600)
       
    