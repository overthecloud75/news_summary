import requests

from configs import NVD_API_KEY, logger
from .util import get_yesterday, get_today

BASE_URL = 'https://services.nvd.nist.gov/rest/json/cves/2.0'

def get_cve_data():

    yesterday = get_yesterday()
    today = get_today()

    # https://nvd.nist.gov/developers/vulnerabilities
    # https://services.nvd.nist.gov/rest/json/cves/2.0/?lastModStartDate=2021-08-04T13:00:00.000%2B01:00&lastModEndDate=2021-10-22T13:36:00.000%2B01:00
    # API URL
    url = f'{BASE_URL}?lastModStartDate={yesterday}T00:00:00.000%2B01:00&lastModEndDate={today}T23:59:59.000%2B01:00&cvssV3Severity=CRITICAL'

    # 요청 보내기
    response = requests.get(url)
    cve_list = []
    if response.status_code == 200:
        data = response.json()
        total_results = data['totalResults'] 
        vulnerabilities = data['vulnerabilities']
        for vul in vulnerabilities:
            cve = vul['cve']
            modified = {
                'id': cve['id'], 
                'published': cve['published'],
                'lastModified': cve['lastModified'], 
                'description': cve['descriptions'][0]['value'], 
                'score': cve['metrics']['cvssMetricV31'][0]['cvssData']['baseScore'],
                'vector': cve['metrics']['cvssMetricV31'][0]['cvssData']['vectorString'], 
                'reference': cve['references'][0]['url']
            }
            cve_list.append(modified)
    else:
        logger.error(response.data)
    return cve_list 