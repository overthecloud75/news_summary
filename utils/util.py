from datetime import datetime, timedelta
import csv

from configs import logger

def make_csv_file(results=[], filename='.csv'):
    today = get_today()
    csv_header = ['no', 'keyword', 'source', 'title', 'content', 'summary', 'content_size', 'summary_size', 'compression_ratio', 'llm_model']
    make_csv_from_data(filename, data=csv_header)

    for i, result in enumerate(results):
        len_content = len(result['content'])
        len_summary = len(result['summary'])
        compression_ratio = round(len_summary / len_content, 3) 
        data = [i + 1, result['keyword'], result['source'], result['title'], result['content'], result['summary'], len_content, len_summary, compression_ratio, result['llm_model']]
        make_csv_from_data(filename, data=data)

def make_csv_from_data(filename, data=[]):
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

def get_yesterday():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d') 

def get_today():
    return datetime.today().strftime('%Y-%m-%d')

def get_hour():
    return datetime.now().hour
