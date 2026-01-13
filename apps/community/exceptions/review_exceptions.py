from rest_framework.exceptions import APIException
from rest_framework import status


# 403
class NotReviewAuthor(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "작성자가 일치하지 않습니다."
    default_code = "not_review_author"
