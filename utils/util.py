from datetime import datetime, timedelta
import csv

from configs import logger

def make_csv_file(results=[], filename='.csv'):
    today = get_today()
    csv_header = ['no', 'source', 'title', 'summary']
    make_csv_from_data(filename, data=csv_header)

    for i, result in enumerate(results):
        data = [i, result['source'], result['title'], result['summary']]
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
