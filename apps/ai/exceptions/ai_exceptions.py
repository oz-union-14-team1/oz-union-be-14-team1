from rest_framework.exceptions import APIException
from rest_framework import status
from django.conf import settings

MIN_COUNT = getattr(settings, "AI_SUMMARY_MIN_REVIEW_COUNT", 10)
MIN_VALID_COUNT = getattr(settings, "AI_SUMMARY_MIN_VALID_REVIEWS", 3)


class NotEnoughReviews(APIException):
    """
    리뷰 개수가 요약 생성 기준(10개) 미만일 때 발생
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        f"리뷰가 부족하여 요약을 생성할 수 없습니다. (최소 {MIN_COUNT}개 필요)"
    )
    default_code = "not_enough_reviews"


class NotEnoughValidReviews(APIException):
    """
    글자 수 조건을 만족하는 '유효한 리뷰'가 부족할 때 발생
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        f"요약에 적합한 긴 리뷰가 부족합니다. (최소 {MIN_VALID_COUNT}개 필요)"
    )
    default_code = "not_enough_valid_reviews"


class AiGenerationFailed(APIException):
    """
    Gemini API 호출 실패 또는 로직 에러 시 발생
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "AI 요약 생성 중 일시적인 오류가 발생했습니다."
    default_code = "ai_generation_failed"


class GameNotFound(APIException):
    """
    게임 ID가 존재하지 않을 때 발생
    (Community 앱에 같은 예외가 존재하지만 의존성 분리를 위해 따로 정의)
    """

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "존재하지 않는 게임입니다."
    default_code = "game_not_found"
