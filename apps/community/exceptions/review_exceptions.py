from rest_framework.exceptions import APIException
from rest_framework import status


# 403
class NotReviewAuthor(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "작성자가 일치하지 않습니다."
    default_code = "not_review_author"


# 404 - 리뷰 없음 예외
class ReviewNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "존재하지 않는 리뷰입니다."
    default_code = "review_not_found"


# 404 - 게임 없음 예외
class GameNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "존재하지 않는 게임입니다."
    default_code = "game_not_found"
