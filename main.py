import os
import time
import sys

from configs import LLM_SERVING, DELIVERY_HOUR, CSV_DIR, NEWS_CATEGORIES, TI_SAVE_URL, NEWS_SAVE_URL, SEND_EMAIL, logger
from ai import Ollama, VLLM
from utils import *

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
        if not os.path.exists(csv_file_path) and hour >= DELIVERY_HOUR:
            try:
                results = get_results_from_ti()
                ti_results = get_ti_summary_from_llm(llm, results)
            except Exception as e:
                logger.error(e)
                ti_results = {'ti_indicator': [], 'ti_description': []}
            try:
                if ti_results['ti_indicator'] or ti_results['ti_description']:
                    save_to_db(TI_SAVE_URL, ti_results)
                    if ti_results['ti_indicator']:
                        make_csv_file(results=ti_results['ti_indicator'], filename=csv_file_path)
                    if ti_results['ti_description']:
                        subject = f'[Threat Intelligence] {today}'
                        html = get_ti_html(subject, results=ti_results['ti_description'], llm_model=llm.model)
                        if html and SEND_EMAIL:
                            send_email(html, subject=subject, attached_file=csv_file_path)
            except Exception as e:
                logger.error(e)

        # NEWS Summary 
        for category in NEWS_CATEGORIES:
            news_file_path = f'{CSV_DIR}/{category}_NEWS_{today}.csv'
            if not os.path.exists(news_file_path) and hour >= DELIVERY_HOUR:
                news_list = []
                try:
                    news = News()
                    news_list = news.read_webdriver(category)
                    # NEWS summary
                    get_news_summary_from_llm(llm, news_list)
                except Exception as e:
                    logger.error(e)
                if news_list:
                    try:
                        save_to_db(NEWS_SAVE_URL, news_list)
                        make_csv_file(results=news_list, filename=news_file_path)
                        '''
                        if SEND_EMAIL:
                            subject = f'[{category} News Summary] {today}'
                            html = get_news_html(subject, category, results=news_list, llm_model=llm.model)
                            send_email(html, subject=subject)
                        '''
                        '''
                        # evaluate category
                            evaluate_category_from_llm(llm, news_list)
                        '''

                        # deep research
                        report_list = deep_research_from_llm(llm, news_list)
                        make_csv_file(results=report_list, filename=f'{CSV_DIR}/{category}_REPORT_{today}.csv')
                        if report_list and SEND_EMAIL:
                            deep_research_subject = f'[{category} deep research] {today}'
                            html = get_deep_research_html(deep_research_subject, category, results=report_list, llm_model=llm.model)
                            send_email(html, subject=deep_research_subject)
                    except Exception as e:
                        logger.error(e)
        # cve_list = get_cve_data()
        time.sleep(3600)
       
    