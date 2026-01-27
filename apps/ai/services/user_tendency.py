import logging
from django.conf import settings
from google import genai
from google.genai import types
from apps.preference.services.preference_list_service import get_user_total_preferences

logger = logging.getLogger(__name__)


class UserTendencyService:
    def __init__(self):
        """
        서비스 초기화: Client 생성 및 공통 설정 정의
        """
        api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-flash-latest"

        self.system_instruction = (
            "당신은 게이머의 성향을 꿰뚫어 보는 게임 심리학자입니다. "
            "유저가 선택한 선호 장르와 태그를 보고, 이 유저가 어떤 스타일의 게이머인지 "
            "한눈에 알 수 있도록 '한국어 10글자 이내'로 명확하고 임팩트 있게 정의해주세요. "
            "무조건 JSON 형식으로만 응답하세요."
        )

    def get_tendency(self, user) -> dict:
        """
        유저의 선호도를 기반으로 성향 분석 (10자 이내)
        """

        preferences = get_user_total_preferences(user)

        genre_names = ", ".join([g.Genre_ko for g in preferences["Genres"]])
        tag_names = ", ".join([t.name for t in preferences["Tags"]])

        if not genre_names and not tag_names:
            return {"tendency": "아직 모르는 게이머"}

        user_prompt = f"""
        이 유저의 게이머 성향을 10글자 이내로 요약해줘.

        [User Preferences]
        - 선호 장르: {genre_names}
        - 선호 태그: {tag_names}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=UserTendency,
                ),
            )
            import json
            return json.loads(response.text)

        except Exception as e:
            logger.error(f"User({user.id}) Tendency Analysis Failed: {e}")
            return {"tendency": "알 수 없는 모험가"}