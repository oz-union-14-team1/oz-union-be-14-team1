import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from google import genai
from google.genai import types
from apps.ai.pydantics import GameSummary
from apps.game.models.game import Game
from apps.ai.models import GameReviewSummary
from apps.ai.exceptions.ai_exceptions import (
    GameNotFound,
    NotEnoughReviews,
    AiGenerationFailed,
)

logger = logging.getLogger(__name__)


class ReviewSummaryService:
    def __init__(self):
        """
        서비스 초기화: Client 생성 및 공통 설정 정의
        """
        api_key = settings.GEMINI_API_KEY

        # 최신 SDK의 Client 인스턴스 생성
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-flash-latest"

        # AI의 페르소나(역할)를 정의
        self.system_instruction = (
            "당신은 20년 경력의 베테랑 게임 전문 리뷰 분석가입니다. "
            "사용자의 리뷰 데이터를 객관적으로 분석하여, "
            "게임의 장단점과 핵심적인 특징을 명확하게 요약해야 합니다. "
            "무조건 JSON 형식으로만 응답하세요."
        )

    def get_summary(self, game_id: int) -> dict:
        """
        외부에서 호출하는 요약 조회 메서드
        """
        try:
            # 게임 ID로 게임 객체를 조회
            game = Game.objects.select_related("summary").get(id=game_id)
        except Game.DoesNotExist:
            # 게임이 없으면 커스텀 예외(404) 발생
            raise GameNotFound()

        review_count = game.reviews.filter(is_deleted=False).count()  # type: ignore

        if review_count < 10:
            # 리뷰가 10개 미만이면 예외(400) 발생
            raise NotEnoughReviews()

        summary_obj = getattr(game, "summary", None)

        # 갱신이 필요한지 확인(필요OX)
        if self._update_and_parse(summary_obj):
            # 갱신이 필요하면 AI 생성 및 저장을 수행하고 결과를 반환
            return self._generate_and_save(game, summary_obj)
        # 갱신이 필요 없으면 DB에 저장된 JSON 텍스트를 파싱하여 반환
        return json.loads(summary_obj.text)  # type: ignore

    def _update_and_parse(self, summary_obj) -> bool:
        """
        요약 데이터 갱신 여부 판단
        """
        # 기존 요약이 없으면 무조건 갱신(생성)
        if not summary_obj:
            return True

        # 현재 시간과 마지막 수정 시간(updated_at)의 차이를 계산
        update_time_difference = timezone.now() - summary_obj.updated_at

        # 마지막 수정일로부터 30일이 지났으면 True를 반환
        return update_time_difference > timedelta(days=30)

    def _generate_and_save(self, game: Game, summary_obj) -> dict:
        """
        AI 요약 생성 및 DB 저장
        """
        # 최신 리뷰 5개를 가져오기
        reviews = game.reviews.filter(is_deleted=False).order_by("-created_at")[:5]  # type: ignore

        # 리뷰 내용들을 줄바꿈 문자로 연결하여 하나의 문자열로 만듬
        reviews_text = "\n".join([f"- {r.content}" for r in reviews])

        # AI에게 보낼 사용자 프롬프트를 구성
        user_prompt = f"""
        게임명: {game.name}
        아래 유저 리뷰들을 분석해서 지정된 JSON 스키마에 맞춰 요약해줘.

        [Review Data]
        {reviews_text}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                # 생성 설정 객체
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,  # 페르소나 적용
                    response_mime_type="application/json",  # 응답 형식을 JSON으로 강제
                    response_schema=GameSummary,  # Pydantic 모델을 스키마로 전달하여 구조 강제
                ),
            )

            # 생성된 JSON 문자열을 가져옴
            result_json_str = response.text

            with transaction.atomic():
                if summary_obj:
                    # 기존 요약이 있다면 내용을 수정
                    summary_obj.text = result_json_str
                    summary_obj.save()
                else:
                    # 없다면 생성
                    GameReviewSummary.objects.create(game=game, text=result_json_str)

            # 저장된 JSON 문자열을 딕셔너리로 변환하여 반환
            return json.loads(result_json_str)

        except Exception as e:
            # 에러 발생 시 로그를 남김
            logger.error(f"Game({game.id}) AI Summary Generation Failed: {e}")

            # 생성에 실패했더라도 기존 캐시가 있다면 반환
            if summary_obj:
                return json.loads(summary_obj.text)

            # 기존 데이터도 없고 생성도 실패했다면 503 예외 발생
            raise AiGenerationFailed()
