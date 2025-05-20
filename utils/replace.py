import re

def remove_leading_br(result):
    # 정규 표현식을 사용하여 맨 앞에 있는 <br> 태그를 제거합니다.
    return re.sub(r'^\s*<br\s*/?>\s*', '', result, flags=re.IGNORECASE)

def strip_useless(result):
    result = result.replace('\n\n', '\n')
    result = remove_leading_br(result.replace('\n', '<br>'))
    result = re.sub(r'\*\*요약:\*\*<br>', '', result)
    result = re.sub(r'\*\*Summary:\*\*<br>', '', result)
    result = re.sub(r'\*\*', '', result)
    result = result.replace('한국어로 요약된 내용:', '')
    result = result.replace('한국어로 요약하자면 다음과 같습니다:', '')
    result = result.replace('요약:<br>', '')
    result = result.replace('요약<br>', '')
    result = result.replace('번역:<br>', '')
    result = result.replace('## 문서 번역 및 ', '')
    result = result.replace('## 문서 요약: ', '') 
    return result