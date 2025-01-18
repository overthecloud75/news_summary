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

CATEGORY = '''다음 문서를 읽고, 문서를 작성한 언어를 아래 카테고리 중 하나로 분류하세요.
카테고리: 
{}

문서: {}
출력은 해당 카테고리 이름만 작성하세요. 
'''