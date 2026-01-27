import logging
import json
from django.conf import settings
from django.db import transaction
from google import genai
from google.genai import types

from apps.ai.models import UserTendency
from apps.ai.pydantics.user_tendency import UserTendency as PydanticUserTendency

from apps.preference.services.preference_list_service import get_user_total_preferences

logger = logging.getLogger(__name__)


class UserTendencyService:
    def __init__(self):
        # API Key가 없는 경우에 대한 방어 로직 (선택 사항)
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            logger.critical("GEMINI_API_KEY is missing in settings.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-flash-latest"

        self.system_instruction = (
            "당신은 게이머의 성향을 꿰뚫어 보는 게임 심리학자입니다. "
            "유저가 선택한 선호 장르와 태그를 보고, 이 유저가 어떤 스타일의 게이머인지 "
            "한눈에 알 수 있도록 '한국어 10글자 이내'로 명확하고 임팩트 있게 정의해주세요. "
            "무조건 JSON 형식으로만 응답하세요."
        )

    def get_or_create_tendency(self, user) -> dict:
        """
        DB에 성향이 있으면 반환하고, 없으면 AI 분석 후 저장하여 반환
        """
        # 1. DB 조회 (캐싱) - related_name 활용
        if hasattr(user, 'ai_tendency'):
            return {"tendency": user.ai_tendency.tendency}

        # 2. AI 분석 및 저장
        return self._analyze_and_save(user)

    def _analyze_and_save(self, user) -> dict:
        preferences = get_user_total_preferences(user)

        # 데이터 전처리: 빈 리스트 방어 로직 강화
        genres = preferences.get("Genres", [])
        tags = preferences.get("Tags", [])

        genre_names = ", ".join([str(g.genre) for g in genres])
        tag_names = ", ".join([str(t.tag) for t in tags])

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
                    response_schema=PydanticUserTendency,
                ),
            )

            result = json.loads(response.text)
            tendency_text = result.get("tendency", "알 수 없는 모험가")

            # 3. DB 저장 (Atomic Transaction 적용)
            # 동시 요청 시 데이터 무결성을 보장합니다.
            with transaction.atomic():
                UserTendency.objects.update_or_create(
                    user=user,
                    defaults={"tendency": tendency_text}
                )

            return {"tendency": tendency_text}

        except Exception as e:
            # 구체적인 에러 내용을 로그에 남김
            logger.error(f"User({user.id}) Tendency Analysis Failed: {e}", exc_info=True)
            return {"tendency": "알 수 없는 모험가"}