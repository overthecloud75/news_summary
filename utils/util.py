from datetime import datetime, timedelta
import csv
import os
import re

from configs import logger

def make_csv_file(results=[], filename='.csv'):
    try:
        csv_header = results[0].keys()
        if not os.path.exists(filename):
            make_csv_from_data(filename, data=csv_header)

        for i, result in enumerate(results):
            data = [i + 1]
            for key in csv_header:
                if key != 'no':
                    data.append(result[key])
            make_csv_from_data(filename, data=data)
    except Exception as e:
        logger.error(e)

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

def is_korean_or_english(query):
    lang_kor = True 
    english_pattern = re.compile(r'[a-zA-Z]+')  
    empty_removed_word = query.replace(' ', '') # 공백 제거
    english_matches = english_pattern.findall(empty_removed_word) 
    if english_matches and empty_removed_word == english_matches[0]:
        lang_kor = False
    return lang_kor

def is_text_korean_or_english(text):
    text_kor = True
    text = text.replace('<br>', '')
    text = text.replace(' ', '')
    len_text = len(text)
    len_korean = 0
    korean_pattern = re.compile(r'[가-힣0-9!?.*-]') 
    for c in text:
        if korean_pattern.search(c):
            len_korean = len_korean + 1
    korean_ratio = round(len_korean / len_text, 2)
    if korean_ratio < 0.5:
        text_kor = False
    return text_kor, korean_ratio
