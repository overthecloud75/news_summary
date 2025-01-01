from selenium import webdriver
import time
import datetime
import requests
import feedparser
from bs4 import BeautifulSoup

from configs import logger, PRODUCTION_MODE, NEWS_KEYWORD_LIST, RELIABLE_NEWS_SOURCE
from .ai import summarize_koren_contents_with_bare_api

def read_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 열지 않고 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    news_list = []

    for query in NEWS_KEYWORD_LIST:
        logger.info(query)
        news_list = news_list + get_rss_google_news_list(query=query)
        if not PRODUCTION_MODE:
            news_list = news_list[0:2]
            logger.info(news_list)

    for news in news_list:
        driver.get(news['link'])
        while True:
            time.sleep(3)
            url = driver.current_url 
            if 'https://news.google.com/rss/articles' not in url:
                logger.info(url)
                html = driver.page_source
                news['url'] = url
                news['summary'] = get_content_from_html(html, news['source'])
                break 
    return news_list

def get_rss_google_news_list(query='보안'):

    logger.info('rss_google_news start')

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    today = today.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d') 

    url = f'https://news.google.com/rss/search?q={query}%20after:{yesterday}%20before:{today}&hl=ko&gl=KR&ceid=KR%3Ako'
    response = requests.get(url)

    news_list = []

    if response.status_code != 200:
        logger.error(response.text)
    else:
        feed = feedparser.parse(response.content)
        news_list = []
        for entry in feed.entries:
            title = entry.title
            title_list = title.split(' - ')
            if len(title_list) == 2:
                news_title = title_list[0]
                source = title_list[1]
                if source in RELIABLE_NEWS_SOURCE:
                    news = {'title': news_title, 'link': entry.link, 'date': entry.published, 'source': source}
                    news_list.append(news)
    return news_list 

def get_content_from_html(html, source):
    soup = BeautifulSoup(html, 'html.parser')
    article = None 
    contents = []
    if source == '보안뉴스':
        article = soup.find('div', id='con')
        if article:
            pass 
        else:
            article = soup.find('div', id='news_content')
    elif source == '디지털타임스':
        article = soup.find('div', class_='article_view')

    if article:
        content = article.get_text(separator=' ', strip=True)
        content = remove_some_content(content, source)
        summary = summarize_koren_contents_with_bare_api(content)
    else:
        summary = ''
    return summary

def remove_some_content(content, source):
    if source == '보안뉴스':
        content = content.replace('<저작권자: 보안뉴스( www.boannews.com ) 무단전재-재배포금지>', '')
        content = content.replace('보안뉴스', '')
        content = content.replace('@boannews.com', '')
    elif source == '디지털타임스':
        content = content.replace('[ 저작권자 ⓒ디지털타임스, 무단 전재 및 재배포 금지 ]', '')
        content = content.replace('[저작권자 ⓒ디지털타임스 무단 전재-재배포 금지]', '')
        content = content.replace('디지털다임스', '')
        content = content.replace('@dt.co.kr', '')
    return content



