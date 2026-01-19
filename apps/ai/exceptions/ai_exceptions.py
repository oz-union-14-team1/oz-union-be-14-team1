from rest_framework.exceptions import APIException
from rest_framework import status


class NotEnoughReviews(APIException):
    """
    리뷰 개수가 요약 생성 기준(10개) 미만일 때 발생
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "리뷰가 부족하여 요약을 생성할 수 없습니다. (최소 10개 필요)"
    default_code = "not_enough_reviews"


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
