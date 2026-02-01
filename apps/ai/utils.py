from google.genai import types
from korcen import korcen  # type: ignore

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


def is_valid_review_for_ai(text: str) -> bool:
    """
    AI 요약에 사용할 리뷰인지 판단합니다.
    - 욕설이 없으면: 무조건 통과
    - 욕설이 있으면: 정보량이 충분한지(길이) 확인하여 통과 여부 결정
    - 사용 가능하면 True, 버려야 하면 False
    """
    # 1. 욕설 여부 확인
    if korcen.check(text):
        # 2. 욕설이 있는데 길이가 짧다면 (ex. "개망겜", "ㅈ노잼") -> 정보 가치 없음, 토큰 낭비
        if len(text) < 10:
            return False

        # 3. 욕설이 있지만 길이가 길다면 (ex. "재미는 있는데 운영이 쓰레기임") -> 정보 가치 있음
        return True

    # 4. 욕설이 없으면 통과
    return True
