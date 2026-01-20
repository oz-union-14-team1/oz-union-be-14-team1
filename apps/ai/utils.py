from google.genai import types


# 1. 욕설 필터 패턴(정규표현식)
BAD_PATTERNS = [
    # 1. "시발" 계열
    r"시[^가-힣]*?발",
    r"씨[^가-힣]*?발",
    # 2. "개새끼" 계열
    r"개[^가-힣]*?새[^가-힣]*?끼",
    r"새[^가-힣]*?끼",
    # 3. "병신" 계열
    r"병[^가-힣]*?신",
    r"븅[^가-힣]*?신",
    # 4. "ㅈ" 계열
    r"좆",
    r"좇",
    r"좃",
    # 5. 패드립 계열
    r"느[^가-힣]*?금[^가-힣]*?마",
    r"느[^가-힣]*?금",
    r"니[^가-힣]*?애[^가-힣]*?미",
    r"니[^가-힣]*?미",
    # 6. "미친" 계열
    r"미[^가-힣]*?친",
    # 7. "지랄/염병" 계열
    r"지[^가-힣]*?랄",
    r"염[^가-힣]*?병",
    # 8. "호로" 계열
    r"호[^가-힣]*?로",
]

# AI 안전 설정
# BLOCK_ONLY_HIGH(최소 차단)
SAFETY_SETTINGS = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,  # 혐오발언
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,  # 괴롭힘
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,  # 선정성
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,  # 위험 콘텐츠
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]
