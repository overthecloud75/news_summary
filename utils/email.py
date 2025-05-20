import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE
from email.encoders import encode_base64
import markdown
import os

from configs import NEWS_KEYWORDS, ACCOUNT, MAIL_SERVER, CC, TO, logger

def send_email(news_html, subject='', attached_file=''):
    if news_html:
        mime_text = MIMEText(news_html, 'html')
        mimemsg = MIMEMultipart()
        mimemsg['From'] = 'SECURITY CENTER' + '<' + ACCOUNT['email'] + '>'
        mimemsg['To'] = TO
        if CC:
            mimemsg['Cc'] = CC
        mimemsg['Subject'] = subject
        mimemsg.attach(mime_text)
        part = None 
        attached_file_path = ''

        if attached_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attached_file,'rb').read())
            encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename={}'.format(attached_file.split('/')[-1]))
            mimemsg.attach(part)
        try:
            connection = smtplib.SMTP(host=MAIL_SERVER['host'], port=MAIL_SERVER['port'])
            connection.ehlo('mylowercasehost')
            connection.starttls()
            connection.ehlo('mylowercasehost')
            if MAIL_SERVER['host'] == 'smtp.office365.com':
                connection.login(ACCOUNT['email'], ACCOUNT['password'])
            connection.send_message(mimemsg)
            connection.quit()
            logger.info('send email')
            return True
        except Exception as e:
            logger.error(e)
            return False
    else:
        return False

def get_news_html(subject, category, results=[], llm_model=''):
    html = '''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Threat Intelligence</title>
        <style>
            .vertical-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .vertical-table th, .vertical-table td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            .vertical-table th {
                background-color: #f2f2f2;
            }
            .vertical-table td {
                vertical-align: top;
            }
            @media (max-width: 600px) {
                table {
                    display: block;
                }
                caption {
                    display: none;
                }
                thead {
                    display: none; /* 헤더 숨기기 */
                }
                tbody, tr, td {
                    display: block;
                    width: 100%;
                }
                tr {
                    margin-bottom: 16px; /* 각 데이터 그룹 간 간격 */
                }
                td {
                    text-align: left;
                    position: relative;
                    padding-left: 50%; /* 헤더를 가상으로 표시할 공간 */
                }
            }
        </style>
    </head>
    <body style='font-family: Arial, sans-serif;'>
    '''

    news_keywords = ''
    for news_keyword in NEWS_KEYWORDS[category]:
        if news_keywords:
            news_keywords = news_keywords + ', ' + news_keyword
        else:
            news_keywords = news_keyword

    html += f'''
        <table class='vertical-table' style='width: 100%; border-collapse: collapse; margin: 20px 0;'>
            <p>출처: Google News</p>
            <p>검색어: {news_keywords}</p>
            <p>LLM({llm_model})으로 기사 요약</p>
            <caption style='font-size: 15px; font-weight: bold; color: #333; text-align: center; margin-bottom: 10px;'>{subject}</caption>
            <thead>
                <tr>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>No</th>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>Title</th>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>Summary</th>
                </tr>
            </thead>
            <tbody>
    '''
    for i, result in enumerate(results):
        if result['summary']:
            html += f'''
                <tr>
                    <td style='text-align: center; border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{i + 1}</td>
                    <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>
                        <a href={result['reference']}>{result['name']}</a><br>- 출처: {result['source']}<br>- keyword: {result['keyword'] + '(' + result['query'] + ')'}
                    </td>                                                                                     
                    <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{result['summary']}</td>
                </tr>
            '''
    html += '''
            </tbody>
        </table>
    </body>
    </html>
    '''

    return html 

def get_deep_research_html(subject, category, results, llm_model=''):
    html = '''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Threat Intelligence</title>
        <style>
            table {
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
        </style>
    </head>
    <body style='font-family: Arial, sans-serif;'>
    '''

    html += f'''
        <p>LLM({llm_model})으로 Deep Research Report 작성</p>
        <br>
    '''
    for result in results:
        html += f'''
        <p>참고 기사 : {result['reference']}
        <hr>
        {markdown.markdown(result['report'], extensions=['markdown.extensions.tables'])}
        <hr>
        <br>
        '''
    html += '''
    </body>
    </html>
    '''

    return html 

def get_ti_html(subject, results=[], llm_model=''):
    html = '''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Threat Intelligence</title>
        <style>
            .vertical-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .vertical-table th, .vertical-table td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            .vertical-table th {
                background-color: #f2f2f2;
            }
            .vertical-table td {
                vertical-align: top;
            }
            @media (max-width: 600px) {
                table {
                    display: block;
                }
                caption {
                    display: none;
                }
                thead {
                    display: none; /* 헤더 숨기기 */
                }
                tbody, tr, td {
                    display: block;
                    width: 100%;
                }
                tr {
                    margin-bottom: 16px; /* 각 데이터 그룹 간 간격 */
                }
                td {
                    text-align: left;
                    position: relative;
                    padding-left: 50%; /* 헤더를 가상으로 표시할 공간 */
                }
            }
        </style>
    </head>
    <body style='font-family: Arial, sans-serif;'>
    '''

    html += f'''
        <table class='vertical-table' style='width: 100%; border-collapse: collapse; margin: 20px 0;'>
            <p>출처: Alien Vault
            <p>LLM({llm_model})으로 description 요약</p>
            <p>첨부 파일의 IOC 정보를 Proxy, Firewall, Anti-Virus에 적용할 수 있습니다.</p>
            <caption style='font-size: 15px; font-weight: bold; color: #333; text-align: center; margin-bottom: 10px;'>{subject}</caption>
            <thead>
                <tr>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>No</th>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>Title</th>
                    <th style='text-align: center; background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px;'>Summary</th>
                </tr>
            </thead>
            <tbody>
    '''
    for i, result in enumerate(results):
        if result['summary']:
            if result['adversary']:
                html += f'''
                    <tr>
                        <td style='text-align: center; border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{i + 1}</td>
                        <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>
                            <a href={result['reference']}>{result['name']}</a><br>- adversary: {result['adversary']}
                        </td>                                                                                     
                        <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{result['summary']}</td>
                    </tr>
                '''
            else:
                html += f'''
                    <tr>
                        <td style='text-align: center; border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{i + 1}</td>
                        <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>
                            <a href={result['reference']}>{result['name']}
                        </td>                                                                                     
                        <td style='border: 1px solid #dddddd; padding: 8px; vertical-align: top;'>{result['summary']}</td>
                    </tr>
                '''
    html += '''
            </tbody>
        </table>
    </body>
    </html>
    '''
    return html

 
    
    