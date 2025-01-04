from selenium import webdriver
import time
import datetime
import requests
import feedparser
from bs4 import BeautifulSoup
import re

from configs import logger, PRODUCTION_MODE, KEYWORD_NEWS_LIMIT, NEWS_KEYWORD_LIST, RELIABLE_NEWS_SOURCE
from .ai import summarize_korean_content_with_bare_api, summarize_english_content_with_bare_api

def read_webdriver():
    logger.info('start webdriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 열지 않고 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    news_list = []

    for query in NEWS_KEYWORD_LIST:
        logger.info(query)
        if PRODUCTION_MODE:
            news_list = news_list + get_rss_google_news_list(query=query)
        else:
            news_list = news_list + get_rss_google_news_list(query=query)[:KEYWORD_NEWS_LIMIT]
        time.sleep(3)

    for news in news_list:
        driver.get(news['link'])
        while True:
            time.sleep(3)
            url = driver.current_url 
            if 'https://news.google.com/rss/articles' not in url:
                logger.info(url)
                html = driver.page_source
                news['url'] = url
                news['summary'] = get_content_from_html(html, news['source'], news['lang_kor'])
                break 
    return news_list

def get_rss_google_news_list(query='보안'):
    logger.info('rss_google_news start')

    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)

    today = today.strftime('%Y-%m-%d')
    yesterday = yesterday.strftime('%Y-%m-%d') 

    lang_kor = is_korean_or_english(query)
    query = query.replace(' ', '%20') #뛰어쓰기  

    if lang_kor:
        url = f'https://news.google.com/rss/search?q={query}%20after:{yesterday}%20before:{today}&hl=ko&gl=KR&ceid=KR%3Ako'
        #url = f'https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR%3Ako'
    else:
        url = f'https://news.google.com/rss/search?q={query}%20after:{yesterday}%20before:{today}'
    logger.info(url)
    response = requests.get(url)

    news_list = []

    if response.status_code != 200:
        logger.error(response.text)
    else:
        feed = feedparser.parse(response.content)
        news_list = []
        source_list = []
        for entry in feed.entries:
            title = entry.title
            title_list = title.split(' - ')
            if len(title_list) == 2:
                news_title = title_list[0]
                source = title_list[1]
                if source in RELIABLE_NEWS_SOURCE:
                    news = {'title': news_title, 'link': entry.link, 'date': entry.published, 'source': source, 'lang_kor': lang_kor}
                    if news not in news_list:
                        news_list.append(news)
                if source not in source_list:
                    source_list.append(source)
        logger.info(f'news_sources: {source_list}')
    return news_list 

def get_content_from_html(html, source, lang_kor):
    soup = BeautifulSoup(html, 'html.parser')
    article = None 
    contents = []
    if source == '보안뉴스':
        article = soup.find('div', id='con')
        if article:
            pass 
        else:
            article = soup.find('div', id='news_content')
    elif source in ['디지털타임스']:
        article = soup.find('div', class_='article_view')
    elif source == '데일리시큐':
        article = soup.find(attrs={'itemprop': 'articleBody'})
    elif source == 'CIO.com':
        article = soup.find('div', id='remove_no_follow')
    elif source == 'CybersecurityNews':
        article = soup.find('div', class_='td-post-content tagdiv-type')
    elif source == 'SecurityInfoWatch':
        article = soup.find('div', class_='html')
    '''
    elif source == 'CyberNews.com':
        article = soup.find('div', class_='section__body')
        article = soup.find(article, class_='content')
    elif source == 'The Hacker News':
        article = soup.find('div', id='articleBody')
    elif source == 'Cybersecurity Dive':
        article = soup.find('div', class_='large medium article-body')
    '''
    if article:
        content = article.get_text(separator=' ', strip=True)
        content = remove_some_content(content, source)
        summary = summarize_content(content, lang_kor)
    else:
        summary = ''
    return summary

def remove_some_content(content, source):
    if source == '보안뉴스':
        content = content.replace('<저작권자: 보안뉴스( www.boannews.com ) 무단전재-재배포금지>', '')
        content = content.replace('보안뉴스', '')
        content = content.replace('@boannews.com', '')
        content = content.replace('3줄 요약', '')
    elif source == '디지털타임스':
        content = content.replace('[ 저작권자 ⓒ디지털타임스, 무단 전재 및 재배포 금지 ]', '')
        content = content.replace('[저작권자 ⓒ디지털타임스 무단 전재-재배포 금지]', '')
        content = content.replace('디지털다임스', '')
        content = content.replace('@dt.co.kr', '')
    elif source == '데일리시큐':
        content = content.replace('저작권자 © 데일리시큐 무단전재 및 재배포 금지', '')
        content = content.replace('▷ 제보 내용 : 보안 관련 어떤 내용이든 제보를 기다립니다! ▷ 광고문의 : jywoo@dailysecu.com ★정보보안 대표 미디어 데일리시큐', '')
        content = content.replace('■ 보안 사건사고 제보 하기 ▷ 이메일 :', '')
        content = content.replace('★정보보안 대표 미디어 데일리시큐', '')
        content = content.replace("/ Dailysecu, Korea's leading security media!★", '')
        content = content.replace("leading security media!★", '')
        content = content.replace('기자 다른기사 보기', '')
        content = content.replace('@dailysecu.com', '')
        content = content.replace('/ Dailysecu, Korea', '')
        content = content.replace('Dailysecu', '')
    elif source == 'CIO.com':
        content = content.replace('dl-ciokorea@foundryco.com', '')
        content = content.replace('@foundryco.com', '')
    logger.info(content)
    logger.info('----')
    return content

def is_korean_or_english(query):
    lang_kor = True 
    english_pattern = re.compile(r'[a-zA-Z]+')  
    empty_removed_word = query.replace(' ', '') # 공백 제거
    english_matches = english_pattern.findall(empty_removed_word) 
    if english_matches and empty_removed_word == english_matches[0]:
        lang_kor = False
    return lang_kor 
    
def summarize_content(content, lang_kor):
    if lang_kor:
        summary = summarize_korean_content_with_bare_api(content)
    else:
        summary = summarize_english_content_with_bare_api(content)
    return summary


