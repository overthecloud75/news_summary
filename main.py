import os
import time
import sys

from configs import LLM_SERVING, DELIVERY_HOUR, DEEP_RESEARCH_MINIMUM_SCORE, CSV_DIR, NEWS_CATEGORIES, CATEGORIES, SYNONYM_DICTIONARY, TI_SAVE_URL, NEWS_SAVE_URL, SEND_EMAIL, logger
from ai import Ollama, VLLM
from utils import get_results_from_ti, News, save_to_db, get_cve_data, get_today, get_hour, make_csv_file, get_ti_html, get_news_html, get_deep_research_html, send_email

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
                results = {'ti_indicator': [], 'ti_description': []}
            try:
                if results['ti_indicator'] or results['ti_description']:
                    save_to_db(TI_SAVE_URL, results)
                    if results['ti_indicator']:
                        make_csv_file(results=results['ti_indicator'], filename=csv_file_path)
                    if results['ti_description']:
                        html = get_ti_html(subject, results=results['ti_description'], llm_model=llm.model)
                        if html and SEND_EMAIL:
                            send_email(html, subject=subject, attached_file=csv_file_path)
            except Exception as e:
                    logger.error(e)

        # NEWS Summary 
        for category in NEWS_CATEGORIES:
            news_file_path = f'{CSV_DIR}/{category}_NEWS_{today}.csv'
            subject = f'[{category} News Summary] {today}'

            if not os.path.exists(news_file_path) and hour >= DELIVERY_HOUR:
                try:
                    news = News()
                    news_list = news.read_webdriver(category)
                    # NEWS summary 
                    news_list = llm.get_news_summary(news_list)
                except Exception as e:
                    logger.error(e)
                    news_list = []
                if news_list:
                    try:
                        save_to_db(NEWS_SAVE_URL, news_list)
                        make_csv_file(results=news_list, filename=news_file_path)
                        '''
                        html = get_news_html(subject, category, results=news_list, llm_model=llm.model)
                        if SEND_EMAIL:
                            send_email(html, subject=subject)
                        '''
                        # evaluate category
                        '''
                        for title in CATEGORIES: 
                            groud_predicted_list = llm.evaluate(title, CATEGORIES[title], news_list)
                            make_csv_file(results=groud_predicted_list, filename=f'{CSV_DIR}/ground_predicted.csv')
                            llm.evaluate(title, CATEGORIES[title], news_list, evaluation_type='few shot')
                            llm.evaluate(title, CATEGORIES[title], news_list, evaluation_type='few shot json')
                        '''
                        # deep research
                        report_points = llm.evaluate_reports(news_list)
                        max_indices = [i for i, v in enumerate(report_points) if v >= DEEP_RESEARCH_MINIMUM_SCORE]
                        deep_research_subject = f'[{category} deep research] {today}'
                        results = []
                        if max_indices and SEND_EMAIL:
                            for max_index in max_indices:
                                report = llm.deep_research(news_list[max_index])
                                if report:
                                    results.append({'reference': news_list[max_index]['reference'], 'report': report})
                            if results:
                                html = get_deep_research_html(deep_research_subject, category, results=results, llm_model=llm.model)
                                send_email(html, subject=deep_research_subject)
                    except Exception as e:
                        logger.error(e)
        # cve_list = get_cve_data()
        time.sleep(3600)
       
    