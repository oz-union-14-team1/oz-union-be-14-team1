import re
from django.core.exceptions import ValidationError


def validate_email_format(value: str):
    """이메일 형식 체크"""
    # ValidationError = 데이터 처리에서 입력된 데이터가 정의된 규칙, 형식 제약조건에 만족하지 못하면 발생하는 오류
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise ValidationError("올바른 이메일 형식이 아닙니다.")


def validate_phone_format(value: str):
    """전화번호 형식 체크 (숫자만,"""
    if not re.match(r"^\d{10,15}$", value):
        raise ValidationError("전화번호 형식이 올바르지 않습니다.")


def validate_nickname_format(value: str):
    """닉네임 길이/문자 체크 (2~16자/ 한글,영문,숫자)"""
    if not (2 <= len(value) <= 16):
        raise ValidationError("닉네임은 2~16자 사이여야합니다.")
    if not re.match(r"^[가-힣a-zA-Z0-9]+$", value):
        raise ValidationError("닉네임은 한글, 영문, 숫자만 가능합니다.")


def validate_user_password(user, password):
    if not user.check_password(password):
        from rest_framework import serializers

        raise serializers.ValidationError("비밀번호가 올바르지 않습니다.")
    return password
