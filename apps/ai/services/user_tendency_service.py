import logging
import json
from django.conf import settings
from django.db import transaction
from google import genai
from google.genai import types
from apps.ai.models import UserTendency
from apps.ai.pydantics.user_tendency import UserTendency as PydanticUserTendency
from django.core.cache import cache



logger = logging.getLogger(__name__)


class UserTendencyService:
    def __init__(self):
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
        API View에서 호출: DB 데이터를 우선 반환하고, 없으면 분석 요청
        """
        from apps.ai.tasks.user_tendency import run_user_tendency_analysis
        if hasattr(user, 'ai_tendency'):
            return {
                "status": "completed",
                "tendency": user.ai_tendency.tendency
            }

        # 2. 캐시 확인 (이미 분석 중인지 체크)
        cache_key = f"debounce_tendency_analysis_{user.id}"
        if cache.get(cache_key):
            # 이미 Task가 돌고 있다면 그냥 "처리 중" 메시지만 반환하고 Task는 실행 X
            return {
                "status": "processing",
                "message": "성향 분석이 진행 중입니다. 잠시만 기다려주세요.",
                "tendency": None
            }

        # 3. 데이터도 없고, 분석 중도 아니라면 -> 분석 요청 (비동기)
        # 캐시 설정 (분석 중임을 표시, 10초 쿨타임)
        cache.set(cache_key, "processing", timeout=10)

        run_user_tendency_analysis.delay(user.id)

        return {
            "status": "processing",
            "message": "성향 분석이 시작되었습니다.",
            "tendency": None
        }

    def analyze_and_save(self, user) -> dict:
        """
        실제 분석 및 DB 저장
        """
        # 순환 참조 방지용 내부 import (필요 시)
        from apps.preference.services.preference_list_service import get_user_total_preferences

        preferences = get_user_total_preferences(user)

        genres = preferences.get("Genres", [])
        tags = preferences.get("Tags", [])

        genre_names = ", ".join([str(g.genre) for g in genres])
        tag_names = ", ".join([str(t.tag) for t in tags])

        if not genre_names and not tag_names:
            return self._save_default(user, "아직 모르는 게이머")

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

            return self._save_to_db(user, tendency_text)

        except Exception as e:
            logger.error(f"User({user.id}) Tendency Analysis Failed: {e}", exc_info=True)
            # 실패 시 에러를 raise 하지 않고 로깅만 남김 (재시도 정책에 따라 변경 가능)
            return {"tendency": "분석 실패"}

    def _save_to_db(self, user, tendency_text: str) -> dict:
        with transaction.atomic():
            UserTendency.objects.update_or_create(
                user=user,
                defaults={"tendency": tendency_text}
            )
        return {"tendency": tendency_text}

    def _save_default(self, user, text: str) -> dict:
        return self._save_to_db(user, text)