import os
import time

from configs import DELIVERY_HOUR, CSV_DIR, NEWS_BASE, SUBJECT_BASE, logger
from utils import read_webdriver, get_cve_data, get_today, get_hour, make_csv_file, send_email

if __name__ == '__main__':
    logger.info('start')
    while True:
        today = get_today()
        hour = get_hour()
        news_file_path = f'{CSV_DIR}/{NEWS_BASE}_{today}.csv'
        if not os.path.exists(news_file_path) and hour >= DELIVERY_HOUR:
            try:
                news_list = read_webdriver()
            except Exception as e:
                logger.error(e)
                news_list = []
            if news_list:
                make_csv_file(results=news_list, filename=news_file_path)
                send_email(news_list, subject= f"{SUBJECT_BASE} {today}")
        # cve_list = get_cve_data()
        time.sleep(3600)
       
    