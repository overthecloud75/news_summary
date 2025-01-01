from datetime import datetime
import csv

from configs import CSV_DIR, CSV_BASE, logger

def make_csv_file(results=[]):
    today = get_today()
    csv_filename = f'{CSV_BASE}_{today}.csv'
    csv_header = ['no', 'source', 'title', 'summary']
    make_csv_from_data(csv_filename, data=csv_header)

    for i, result in enumerate(results):
        data = [i, result['source'], result['title'], result['summary']]
        make_csv_from_data(csv_filename, data=data)
    return csv_filename

def make_csv_from_data(csv_filename, data=[]):
    with open(CSV_DIR + '/' + csv_filename, 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

def get_today():
    return datetime.today().strftime('%Y-%m-%d')
