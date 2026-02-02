import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from google import genai
from google.genai import types

from apps.ai.models.game_review_summary import GameReviewSummary
from apps.ai.pydantics.review_summary import GameSummary

from apps.ai.utils import SAFETY_SETTINGS, is_valid_review_for_ai
from apps.core.utils import query_debugger
from apps.game.models.game import Game

from apps.ai.exceptions.ai_exceptions import (
    GameNotFound,
    NotEnoughReviews,
    AiGenerationFailed,
    NotEnoughValidReviews,
)
from django.db.models.functions import Length

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

        # 환경변수 혹은 settings에서 값을 가져옴, 없을 경우 기본값(default)을 사용
        self.min_review_count = getattr(settings, "AI_SUMMARY_MIN_REVIEW_COUNT", 10)
        self.update_interval_days = getattr(
            settings, "AI_SUMMARY_UPDATE_INTERVAL_DAYS", 30
        )
        self.min_review_length = getattr(settings, "AI_REVIEW_MIN_LENGTH", 10)
        self.min_valid_reviews = getattr(settings, "AI_SUMMARY_MIN_VALID_REVIEWS", 3)
        self.summary_review_count = getattr(settings, "AI_SUMMARY_REVIEW_COUNT", 5)

        # AI의 페르소나(역할)를 정의
        self.system_instruction = (
            "당신은 20년 경력의 베테랑 게임 전문 리뷰 분석가입니다. "
            "사용자의 리뷰 데이터를 객관적으로 분석하여, "
            "게임의 장단점과 핵심적인 특징을 명확하게 요약해야 합니다. "
            # 2차 필터링
            "리뷰 원문에 비속어, 은어, 공격적인 표현이 포함되어 있더라도 "
            "절대로 요약 결과에는 그대로 포함하지 마세요. "
            "해당 표현은 무시하거나, 격식 있고 정중한 표현으로 순화하여 요약해야 합니다. "
            "무조건 JSON 형식으로만 응답하세요."
        )

        # AI에게 보낼 사용자 프롬프트
        self.user_prompt_template = (
            "게임명: {game_name}\n"
            "아래 유저 리뷰들을 분석해서 지정된 JSON 스키마에 맞춰 요약해줘.\n\n"
            "[Review Data]\n"
            "{reviews_text}"
        )

    def get_summary(self, game_id: int) -> dict:
        """
        외부에서 호출하는 요약 조회 메서드
        """
        try:
            game = Game.objects.select_related("summary").get(id=game_id)
        except Game.DoesNotExist:
            raise GameNotFound()

        summary_obj = getattr(game, "summary", None)

        # 2. 갱신이 필요한지 체크
        if not self._update_and_parse(summary_obj):
            # 갱신 필요 없으면 바로 리턴!
            return json.loads(summary_obj.text)  # type: ignore

        # 3. 요약본이 없거나 갱신이 필요할 때만 리뷰 개수 체크
        review_count = game.reviews.filter(is_deleted=False).count()
        if review_count < self.min_review_count:
            raise NotEnoughReviews()

        # 4. 생성 및 저장
        return self._generate_and_save(game, summary_obj)

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
        return update_time_difference > timedelta(days=self.update_interval_days)

    def _build_user_prompt(self, game_name: str, reviews_text: str) -> str:
        return self.user_prompt_template.format(
            game_name=game_name, reviews_text=reviews_text
        )

    def _generate_and_save(self, game: Game, summary_obj) -> dict:
        """
        AI 요약 생성 및 DB 저장
        """
        # 글자 수 필터링 및 유효 리뷰 개수 확인
        bring_reviews = (
            game.reviews.annotate(text_len=Length("content"))  # type: ignore
            .filter(is_deleted=False, text_len__gte=self.min_review_length)
            .order_by("-created_at")[:20]
        )

        clean_reviews = []
        for review in bring_reviews:
            # 욕설 포함여부만 판단
            if not is_valid_review_for_ai(review.content):
                continue  # 유효하지 않은(짧은 욕설 등) 리뷰는 건너뜀

            clean_reviews.append(review)

            if len(clean_reviews) >= self.summary_review_count:
                break

        # 유효한 리뷰가 설정된 개수(예: 3개) 미만이면 중단
        if len(clean_reviews) < self.min_valid_reviews:
            logger.warning(
                f"Game({game.id}) has enough raw reviews but VALID reviews({len(clean_reviews)}) "
                f"are less than {self.min_valid_reviews}."
            )
            raise NotEnoughValidReviews()

        # 리뷰 내용들을 줄바꿈 문자로 연결하여 하나의 문자열로 만듬
        reviews_text = "\n".join([f"- {r.content}" for r in clean_reviews])

        # AI에게 보낼 사용자 프롬프트를 구성
        user_prompt = self._build_user_prompt(game.name, reviews_text)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                # 생성 설정 객체
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,  # 페르소나 적용
                    response_mime_type="application/json",  # 응답 형식을 JSON으로 강제
                    response_schema=GameSummary,  # Pydantic 모델을 스키마로 전달하여 구조 강제
                    safety_settings=SAFETY_SETTINGS,  # 안전 설정 적용
                ),
            )

            # 생성된 JSON 문자열을 가져옴
            result_json_str = response.text

            if summary_obj:
                # 기존 요약이 있다면 내용을 수정
                summary_obj.text = result_json_str
                summary_obj.save(update_fields=["text", "updated_at"])
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
