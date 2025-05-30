from selenium import webdriver
from selenium_stealth import stealth
import trafilatura
import time
import requests
import feedparser
from bs4 import BeautifulSoup
import os

from configs import logger, PRODUCTION_MODE, NEWS_KEYWORD_LIMIT, NEWS_KEYWORDS, RELIABLE_NEWS_SOURCE, TRAF_EXCEPTION_NEWS_SOURCE, ERROR_DIR
from .util import get_yesterday, get_today, is_korean_or_english

class News():
    def __init__(self):
        self.logger = logger 
        self.logger.info('News start!')
        self.driver = None 
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        try:
            self._initialize_webdriver()
        except Exception as e:
            self.logger.error(e)
            self.logger.error('intitilize webdriver failed')
            os.system('pkill -f chromedriver')  
            os.system('pkill -f chrome')
            os.system('pkill -f chromium')

    def _initialize_webdriver(self):
        self.logger.info('start webdriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 브라우저 창을 열지 않고 실행
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)

        stealth(self.driver,
            languages=['en-US', 'en'],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer='Intel Iris OpenGL Engine',
            fix_hairline=True,
        )

    def read_webdriver(self, category):

        news_list = []
        news_title_list = []
        dedup_news_list = []

        if self.driver:
            self.logger.info('read webdriver')

            for keyword in NEWS_KEYWORDS[category]:
                for query in NEWS_KEYWORDS[category][keyword]:
                    self.logger.info(query)
                    if PRODUCTION_MODE:
                        news_list = news_list + self.get_rss_google_news_list(category, query=query, keyword=keyword)
                    else:
                        news_list = news_list + self.get_rss_google_news_list(category, query=query, keyword=keyword)[:NEWS_KEYWORD_LIMIT]
                    time.sleep(3)

            for news in news_list:
                if news['name'] not in news_title_list:   # 중복 기사 제거 
                    news_title_list.append(news['name'])  
                    try:
                        self.driver.get(news['link'])
                        while True:
                            time.sleep(3)
                            url = self.driver.current_url 
                            if 'https://news.google.com/rss/articles' not in url:
                                self.logger.info(url)
                                html = self.driver.page_source
                                if 'Verify you are human' not in html and 'Verifying you are human' not in html:  # check you are human verification
                                    news['reference'] = url
                                    if news['source'] not in TRAF_EXCEPTION_NEWS_SOURCE:
                                        news['content'] = self.get_content_from_url(url, news['source'])
                                    if not news['content']: 
                                        news['content'] = self.get_content_from_html(html, news['source'])  # news soruce 별 parsing 필요 
                                    if news['content']:
                                        dedup_news_list.append(news)
                                else:
                                    self.logger.error('Verify you are human') 
                                break 
                    except Exception as e:
                        self.logger.error(news['link'])
                        self.logger.error(e)
                        self.driver.quit()
                        self._initialize_webdriver()
            self.driver.quit()
            self.logger.info('driver quit')
        return dedup_news_list

    def get_rss_google_news_list(self, category, query='보안', keyword='관제'):
        self.logger.info('rss_google_news start')

        yesterday = get_yesterday()
        today = get_today()

        lang_kor = is_korean_or_english(query)
        query_space = query.replace(' ', '%20') #뛰어쓰기  

        if lang_kor:
            url = f'https://news.google.com/rss/search?q={query_space}%20after:{yesterday}%20before:{today}&hl=ko&gl=KR&ceid=KR%3Ako'
        else:
            url = f'https://news.google.com/rss/search?q={query_space}%20after:{yesterday}%20before:{today}'
        self.logger.info(url)
        response = requests.get(url, self.headers)

        news_list = []

        if response.status_code != 200:
            self.logger.error(response.text)
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
                        news = {'keyword': keyword, 'name': news_title, 'link': entry.link, 'date': entry.published, 'source': source, 'lang_kor': lang_kor, 'query': query, 'category': category, 'content': ''}
                        if news not in news_list:
                            news_list.append(news)
                    if source not in source_list:
                        source_list.append(source)
            self.logger.info(f'news_sources: {source_list}')
        return news_list 

    def get_content_from_url(self, url, source, redirect=False):
        try:
            if redirect:
                response = requests.get(url, self.headers, allow_redirects=True)
                url = response.url
                self.logger.info(url)
            downloaded = trafilatura.fetch_url(url)
            if not downloaded or downloaded == 'None':
                content = None 
            else:
                content = trafilatura.extract(downloaded)
                content = self.remove_some_content(content, source)
        except Exception as e:
            self.logger.error(e)
            content = None 
        return content

    def get_content_from_html(self, html, source):
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
        elif source in ['AI타임스', '인공지능신문', '더에이아이(THE AI)']:
            article = soup.find('article', id='article-view-content-div')
        elif source == 'Security & Intelligence 이글루코퍼레이션':
            div_content = soup.find('div', id='content')
            article = self.get_p_text_in_div_content(div_content)
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
            article = self.get_p_text_in_div_content(div_content)
        elif source == 'SecurityWeek':
            div_content = soup.find('div', class_='zox-post-body')
            article = self.get_p_text_in_div_content(div_content)
        elif source == 'Cybersecurity Dive':
            div_content = soup.find('div', class_='article-body')
            article = self.get_p_text_in_div_content(div_content)
        elif source == 'GBHackers':
            div_content = soup.find('div', class_='tdb_single_content')
            article = self.get_p_text_in_div_content(div_content)
        elif source == 'DevOps.com':
            div_content = soup.find('div', class_='entry-content')
            article = self.get_p_text_in_div_content(div_content)
        elif source == 'Towards Data Science':
            div_content = soup.find('article')
            article = self.get_div_text_in_div_content(div_content)
        if article:
            if type(article) == str:
                content = article
            else: 
                content = article.get_text(separator=' ', strip=True)
            content = self.remove_some_content(content, source)
        else:
            content = ''
        if not content:
            self.logger.error('plz check html!')
            today = get_today()
            filename = source + '_' +  today + '_' + str(time.time())[:10] + '.html'
            with open(ERROR_DIR + '/' + filename, 'w', encoding='utf-8-sig') as f:
                f.write(html)
        return content

    def remove_some_content(self, content, source):
        if source == '보안뉴스':
            content = content.replace('<저작권자: 보안뉴스( www.boannews.com ) 무단전재-재배포금지>', '')
            content = content.replace('<저작권자: (www.boannews.com) 무단전재-재배포금지>', '')
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
            content = content.replace('Copyright ⓒ . 무단전재 및 재배포 금지', '')
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
            content = content.replace('How SOC Teams Save Time and Effort with ANY.RUN', '')
            content = content.replace('Vulnerability Attack Simulation on How Hackers Rapidly Probe Websites for Entry Points', '')
            content = content.replace('Live webinar for SOC teams and managers', '')
            content = content.replace('Free Webinar', '')
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
        return content

    def get_p_text_in_div_content(self, div_content):
        article = ''
        if div_content:
            paragraphs = div_content.find_all('p')
            for p in paragraphs:
                if article:
                    article = article + ' ' + p.text      
                else:
                    article = p.text
        return article

    def get_div_text_in_div_content(self, div_content):
        article = ''
        if div_content:
            paragraphs = div_content.find_all('div')
            for div in paragraphs:
                if article:
                    article = article + ' ' + div.text      
                else:
                    article = div.text
        return article
