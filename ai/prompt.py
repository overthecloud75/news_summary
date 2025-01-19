SUMMARY_KOREAN_TO_KOREAN = '''이 문서의 주요 내용을 요약해 주세요. 요약은 간결하게 하되, 문서의 핵심 정보를 포함해야 하며 고유 명사를 제외하고는 한국어로 표시가 되어야 합니다.

문서: {}

요약:
'''

SUMMARY_ENGLISTH_TO_KOREAN = '''Without line break and key points, Please summarize the following text into Korean. the summary must be in Korean.

Text: {}

요약:
'''

CATEGORY_PROMPT = '''다음 문서를 읽고 아래 카테고리 중 하나로 분류하세요.
카테고리:
{}

문서: {}

출력은 해당 카테고리 이름만 작성하세요. 
'''

CATEGORY_FEW_PROMPT = '''당신은 전문적인 텍스트 분류기입니다. 주어진 텍스트를 미리 정의된 카테고리 중 하나로 분류하고, 각 카테고리에 대한 확률을 계산하세요.

### 카테고리:
{}

다음 텍스트에 대해 출력하세요:
1. 예측된 카테고리.
2. 각 카테고리에 대한 확률 점수(0과 1 사이).

### 출력 예시:
카테고리: 스포츠
확률:
- 스포츠: 0.90
- 정치: 0.05  
- 기타: 0.05

### 입력:
{}
'''

CATEGORY_FEW_JSON_PROMPT = '''당신은 전문적인 텍스트 분류기입니다. 
주어진 텍스트를 미리 정의된 카테고리 중 가장 높은 수치의 하나로 분류하고, 각 카테고리에 대한 확률을 계산하세요. 
출력은 반드시 JSON 형식으로 작성하세요.

### 카테고리:
{}

다음 텍스트에 대해 JSON 형식으로 출력하세요:
predicted 키에는 예측된 카테고리의 이름을 포함하세요.
probabilities 키에는 각 카테고리와 해당 확률을 포함한 딕셔너리를 작성하세요.

### 입력:
{}

### 출력 예시:
```json
{{
  "predicted": "스포츠",
  "probabilities": {{
    "스포츠": 0.85,
    "정치": 0.13,
    "기타": 0.02
  }}
}}
```
'''

