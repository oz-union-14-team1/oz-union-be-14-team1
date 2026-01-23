from rest_framework.exceptions import APIException
from rest_framework import status


class DuplicateUserException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "이미 중복된 회원가입 내역이 존재합니다."
    default_code = "duplicate_user"
