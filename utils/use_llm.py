import re
import time

from .util import get_yesterday, get_today, make_csv_file
from configs import logger, DEEP_RESEARCH_MINIMUM_SCORE, SYNONYM_DICTIONARY, CATEGORIES, CSV_DIR

def get_ti_summary_from_llm(llm, results):
    logger.info('ti summary start!')
    ti_results = {
        'ti_indicator': [],
        'ti_description': [],
    }
    yesterday = get_yesterday()
    for result in results:
        try:
            created = result['created'].split('.')[0]+'z'
            modified = result['modified'].split('.')[0]+'z'
            indicators = result['indicators']
            if result['malware_families']:
                malware_family = result['malware_families'][0]
            else:
                malware_family = ''
            if result['references']:
                reference = result['references'][0]
            else:
                reference = ''
            if yesterday in modified:
                for indicator in indicators:        
                    # save indicator 
                    ti_results['ti_indicator'].append({'id': result['id'], 'modified': modified, 'name': result['name'], 'adversary': result['adversary'], 
                        'indicator': indicator['indicator'].replace('.', '[.]'), 'type': indicator['type'], 'malware_family': malware_family})
                summary = llm.summarize_content(result['description'], False)
                ti_results['ti_description'].append({'id': result['id'], 'created': created, 'modified': modified, 'name': result['name'], 'description': result['description'], 
                    'summary': summary, 'adversary': result['adversary'], 'malware_family': malware_family, 'reference': reference})
        except Exception as e:
            logger.error(e)
    return ti_results 

def get_news_summary_from_llm(llm, news_list):
    logger.info('news summary start!')
    for news in news_list:
        news['llm_model'] = llm.model
        if news['content']:
            news['summary'] = llm.summarize_content(news['content'], news['lang_kor'])
        else:
            news['summary'] = ''
        news['content_size'] = len(news['content'])
        news['summary_size'] = len(news['summary'])
        if news['content_size']:
            news['compression_ratio'] = round(news['summary_size'] / news['content_size'], 3)
        else:
            news['compression_ratio'] = 0 
            logger.info(f'''content size: 0, content: \n{news['content']}''')
    return news

def evaluate_category_from_llm(llm, news_list):
    for title in CATEGORIES: 
        groud_predicted_list = evaluate_from_llm(llm, title, CATEGORIES[title], news_list)
        make_csv_file(results=groud_predicted_list, filename=f'{CSV_DIR}/ground_predicted.csv')
        evaluate_from_llm(llm, title, CATEGORIES[title], news_list, evaluation_type='few shot')
        evaluate_from_llm(llm, title, CATEGORIES[title], news_list, evaluation_type='few shot json')

def evaluate_from_llm(llm, title, cateogories, news_list, evaluation_type='zero shot'):
    logger.info(f'''{title} {evaluation_type} llm evaluate start!''')
    ground_predicted_list = []
    for news in news_list:
        try:
            ground_predicted = {'title': title, 'timestamp': get_today() + '_' + str(time.time())[:10]}
            if title == 'news': 
                if news['query'] in SYNONYM_DICTIONARY:
                    ground_predicted['ground'] = SYNONYM_DICTIONARY[news['query']]
                else:
                    ground_predicted['ground'] = news['query']
            elif title == 'language':
                if news['lang_kor']:
                    ground_predicted['ground'] = '한국어'
                else: 
                    ground_predicted['ground'] = '영어'
            ground_predicted['predicted'] = llm.category_predict(cateogories, title, news, evaluation_type=evaluation_type)
            ground_predicted['source'] = news['source']
            ground_predicted['name'] = news['name']
            ground_predicted['reference'] = news['reference']
            ground_predicted_list.append(ground_predicted)
            logger.info(f'''ground: {ground_predicted['ground']}, 'predicted': {ground_predicted['predicted']}''')
        except Exception as e:
            logger.error(e)
    return ground_predicted_list

def evaluate_reports_from_llm(llm, news_list):
    logger.info(f'''llm evaluate reports start!''')
    ground_predicted_list = []
    for news in news_list:
        try:
            result = llm.evaluate_report(news)
            logger.info('report 설명: {}'.format(result))
            news['score'] = get_point_from_result(result)
            ground_predicted_list.append(news['score'])
        except Exception as e:
            logger.error(e)
    return ground_predicted_list

def deep_research_from_llm(llm, news_list):
    report_list = []
    report_points = evaluate_reports_from_llm(llm, news_list)
    satisfied_indices = [i for i, v in enumerate(report_points) if v >= DEEP_RESEARCH_MINIMUM_SCORE]
    if satisfied_indices:
        for satisfied_index in satisfied_indices:
            news = news_list[satisfied_index]
            report = llm.deep_research(news)
            if report:
                report_list.append({'date': news['date'], 'name': news['name'], 'reference': news['reference'], 'content': news['content'], 'report': report, 'score': news['score']})
    return report_list
   
def get_point_from_result(result):
    pattern = r'(총점|점수|평가|결과):\*?\*?\s*(\d+)\s*(?:/|\점|점)?\s*(?:\d+)?'
    match = re.search(pattern, result)
    try:
        if match:
            score = int(match.group(2))
            logger.info('score: {}'.format(score))
            if score <= 100:
                return score
            else:
                return 0 
        else:
            logger.error('score를 찾을 수 없습니다.')
            return 0
    except Exception as e:
        logger.error(e)
        return 0 


       
