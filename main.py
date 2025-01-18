import os
import time
import sys

from configs import LLM_SERVING, DELIVERY_HOUR, CSV_DIR, NEWS_CATEGORIES, TI_SAVE_URL, NEWS_SAVE_URL, logger
from ai import Ollama, VLLM
from utils import get_results_from_ti, read_webdriver, save_to_db, get_cve_data, get_today, get_hour, make_csv_file, get_ti_html, get_news_html, send_email

if __name__ == '__main__':
    logger.info('start')
    while True:
        today = get_today()
        hour = get_hour()

        # LLM SERVING 
        if LLM_SERVING == 'ollama':
            llm = Ollama()
        elif LLM_SERVING == 'vllm':
            llm = VLLM()
        else:
            logger.error('There is no proper LLM_SERVING.')
            sys.exit()

        # threat intelligence 
        csv_file_path = f'{CSV_DIR}/TI_{today}.csv'
        subject = f'[Threat Intelligence] {today}'

        if not os.path.exists(csv_file_path) and hour >= DELIVERY_HOUR:
            try:
                results = get_results_from_ti()
                results = llm.get_ti_summary(results)
            except Exception as e:
                logger.error(e)
                results = []
            if results:
                try:
                    save_to_db(TI_SAVE_URL, results)
                    make_csv_file(results=results['ti_indicator'], filename=csv_file_path)
                    html = get_ti_html(subject, results=results['ti_description'], llm_model=llm.model)
                    if html:
                        send_email(html, subject=subject, attached_file=csv_file_path)
                except Exception as e:
                        logger.error(e)

        # NEWS Summary 
        for category in NEWS_CATEGORIES:
            news_file_path = f'{CSV_DIR}/{category}_NEWS_{today}.csv'
            subject = f'[{category} News Summary] {today}'
        
            if not os.path.exists(news_file_path) and hour >= DELIVERY_HOUR:
                try:
                    news_list = read_webdriver(category)
                    news_list = llm.get_news_summary(news_list)
                except Exception as e:
                    logger.error(e)
                    news_list = []
                if news_list:
                    try:
                        save_to_db(NEWS_SAVE_URL, news_list)
                        make_csv_file(results=news_list, filename=news_file_path)
                        html = get_news_html(subject, category, results=news_list, llm_model=llm.model)
                        send_email(html, subject=subject)
                        #send_email(news_html, subject=subject, attached_file=news_file_path)
                    except Exception as e:
                        logger.error(e)
            # cve_list = get_cve_data()
        time.sleep(3600)
       
    