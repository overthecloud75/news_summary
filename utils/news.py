from selenium import webdriver
from selenium_stealth import stealth
import time
import requests
import feedparser
from bs4 import BeautifulSoup
import re

from configs import logger, PRODUCTION_MODE, NEWS_KEYWORD_LIMIT, NEWS_KEYWORDS, RELIABLE_NEWS_SOURCE
from .util import get_yesterday, get_today

def read_webdriver(category):
    logger.info('start webdriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 열지 않고 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    news_list = []
    news_title_list = []
    dedup_news_list = []

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    for keyword in NEWS_KEYWORDS[category]:
        for query in NEWS_KEYWORDS[category][keyword]:
            logger.info(query)
            if PRODUCTION_MODE:
                news_list = news_list + get_rss_google_news_list(category, query=query, keyword=keyword)
            else:
                news_list = news_list + get_rss_google_news_list(category, query=query, keyword=keyword)[:NEWS_KEYWORD_LIMIT]
            time.sleep(3)

    for news in news_list:
        if news['name'] not in news_title_list:   # 중복 기사 제거 
            news_title_list.append(news['name'])  
            driver.get(news['link'])
            while True:
                time.sleep(3)
                url = driver.current_url 
                if 'https://news.google.com/rss/articles' not in url:
                    logger.info(url)
                    html = driver.page_source
                    news['reference'] = url
                    news['content'] = get_content_from_html(html, news['source'], news['lang_kor'])
                    if news['content']:
                        dedup_news_list.append(news)
                    break 
    driver.quit()
    logger.info('driver quit')
    return dedup_news_list

def get_rss_google_news_list(category, query='보안', keyword='관제'):
    logger.info('rss_google_news start')

    yesterday = get_yesterday()
    today = get_today()

    lang_kor = is_korean_or_english(query)
    query_space = query.replace(' ', '%20') #뛰어쓰기  

    if lang_kor:
        url = f'https://news.google.com/rss/search?q={query_space}%20after:{yesterday}%20before:{today}&hl=ko&gl=KR&ceid=KR%3Ako'
        #url = f'https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR%3Ako'
    else:
        url = f'https://news.google.com/rss/search?q={query_space}%20after:{yesterday}%20before:{today}'
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
                if source in RELIABLE_NEWS_SOURCE[category]:
                    news = {'keyword': keyword, 'name': news_title, 'link': entry.link, 'date': entry.published, 'source': source, 'lang_kor': lang_kor, 'query': query}
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
    elif source == '디지털데일리':
        article = soup.find('div', class_='article_content')
    elif source in ['AI타임스', '인공지능신문']:
        article = soup.find('article', id='article-view-content-div')
    elif source == 'Security & Intelligence 이글루코퍼레이션':
        div_content = soup.find('div', id='content')
        article = get_p_text_in_div_content(div_content)
    elif source == 'CIO.com':
        article = soup.find('div', id='remove_no_follow')
    elif source == 'CybersecurityNews':
        article = soup.find('div', class_='td-post-content tagdiv-type')
    elif source == 'SecurityInfoWatch':
        article = soup.find('div', class_='html')
    elif source == 'The Hacker News':
        article = soup.find('div', id='articlebody')
    elif source == 'CSO Online':
        article = soup.find('div', class_='article__main')
    elif source == 'CyberNews.com':
        article = soup.find('div', class_='section__body')
    elif source == 'Security Intelligence':
        div_content = soup.find('main', id='post__content')
        article = get_p_text_in_div_content(div_content)
    elif source == 'SecurityWeek':
        div_content = soup.find('div', class_='zox-post-body')
        article = get_p_text_in_div_content(div_content)
    elif source == 'Cybersecurity Dive':
        div_content = soup.find('div', class_='article-body')
        article = get_p_text_in_div_content(div_content)
    elif source == 'GBHackers':
        div_content = soup.find('div', class_='tdb_single_content')
        article = get_p_text_in_div_content(div_content)
    elif source == 'Towards Data Science':
        div_content = soup.find('article')
        article = get_div_text_in_div_content(div_content)
    if article:
        if type(article) == str:
            content = article
        else: 
            content = article.get_text(separator=' ', strip=True)
        content = remove_some_content(content, source)
    else:
        content = ''
    return content

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
        content = content.replace("leading security media!★", '')
        content = content.replace('기자 다른기사 보기', '')
        content = content.replace('@dailysecu.com', '')
        content = content.replace('Dailysecu', '')
    elif source == '디지털데일리':
        content = content.replace('디지털데일리', '')
    elif source == 'Security & Intelligence 이글루코퍼레이션':
        content = content.replace('전문화된 보안 관련 자료, 보안 트렌드를 엿볼 수 있는 차세대 통합보안관리 기업 이글루코퍼레이션 보안정보입니다.', '')
    elif source == 'AI타임스':
        content = content.replace('@aitimes.com', '')
    elif source == '인공지능신문':
        content = content.replace('이미지:본지DB ', '')
    elif source == 'CIO.com':
        content = content.replace('dl-ciokorea@foundryco.com', '')
        content = content.replace('@foundryco.com', '')
    elif source == 'CybersecurityNews':
        content = content.replace('Investigate Real-World Malicious Links', '')
        content = content.replace('Malware & Phishing Attacks With ANY.RUN', '')
        content = content.replace('Try for Free', '')
    elif source == 'The Hacker News':
        content = content.replace('Found this article interesting?', '')
        content = content.replace('Follow us on Twitter  and LinkedIn to read more exclusive content we post.', '')
    elif source == 'GBHackers':
        content = content.replace('Find this News Interesting! Follow us on Google News, LinkedIn, and X to Get Instant Updates!', '')
    elif source == 'Towards Data Science':
        content = content.replace('Follow Towards Data Science', '')
        content = content.replace('Listen Share', '')
        content = content.replace('ListenShare', '')
        content = content.replace('TDS Editors  Newsletter', '')
        content = content.replace('Feeling inspired to write your first TDS post?', '')
        content = content.replace('We’re always open to contributions from new authors', '')
        content = content.replace('FollowPublished inTowards Data Science', '')
        content = content.replace('Published inTowards Data Science', '')
        content = content.replace('don’t hesitate to share it with us', '')
        content = content.replace('Thank you for supporting the work of our authors!', '')
        content = content.replace('As we mentioned above, we love publishing articles from new authors', '')
        content = content.replace('TDS Team', '')
        content = content.replace('TDS Editors', '')
        content = content.replace('Sent as aNewsletter', '')
        content = content.replace('Member-only story', '')
        content = content.replace('·Follow', '')
        content = content.replace('Listen Listen', '')
        content = content.replace('Share Share', '')
        content = content.replace('Until the next Variable', '')
    logger.info(content)
    logger.info('----')
    return content

def get_p_text_in_div_content(div_content):
    article = ''
    if div_content:
        paragraphs = div_content.find_all('p')
        for p in paragraphs:
            if article:
                article = article + ' ' + p.text      
            else:
                article = p.text
    return article

def get_div_text_in_div_content(div_content):
    article = ''
    if div_content:
        paragraphs = div_content.find_all('div')
        for div in paragraphs:
            if article:
                article = article + ' ' + div.text      
            else:
                article = div.text
    return article

def is_korean_or_english(query):
    lang_kor = True 
    english_pattern = re.compile(r'[a-zA-Z]+')  
    empty_removed_word = query.replace(' ', '') # 공백 제거
    english_matches = english_pattern.findall(empty_removed_word) 
    if english_matches and empty_removed_word == english_matches[0]:
        lang_kor = False
    return lang_kor 

