import re
from django.core.exceptions import ValidationError

def validate_email_format(value:str):
    """이메일 형식 체크"""
    # ValidationError = 데이터 처리에서 입력된 데이터가 정의된 규칙, 형식 제약조건에 만족하지 못하면 발생하는 오류
    if not re.match("[^@]+@[^@]+\.[^@]+", value):
        raise ValidationError("올바른 이메일 형식이 아닙니다.")

def validate_phone_format(value:str):
    """전화번호 형식 체크 (숫자만, """
    if not re.match(r"^\d{10,15}$", value):
        raise ValidationError("전화번호 형식이 올바르지 않습니다.")

def validate_nickname_length(value:str):
    """닉네임 길이 체크 (2~16자)"""
    if len(value) < 2 or len(value) > 16:
        raise ValidationError("닉네임은 2~16자 사이여야합니다.")