from typing import Any, Dict, TypedDict

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from datetime import datetime

from apps.user.models.validators import (
    validate_email_format,
    validate_phone_format,
    validate_nickname_format,
)

User = get_user_model()

#### 금지 닉네임 리스트
FORBIDDEN_NICKNAMES = ["admin", "관리자", "test", "운영자"]


#### 임시 인증 코드 저장소 (Redis 사용전까지 사용할 예정)
class EmailCode(TypedDict):
    code: str
    expires: datetime


class PhoneCode(TypedDict):
    code: str
    expires: datetime
    count: int


TEMP_EMAIL_CODES: Dict[str, EmailCode] = {}
TEMP_PHONE_CODES: Dict[str, PhoneCode] = {}


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email_code = serializers.CharField(write_only=True)
    phone_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "nickname",
            "phone_number",
            "gender",
            "password",
            "password_confirm",
            "email_code",
            "phone_code",
        ]

    #### 이메일 검증
    def validate_email(self, value: str) -> str:
        try:
            validate_email_format(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value

    #### 닉네임 검증
    def validate_nickname(self, value: str) -> str:
        try:
            validate_nickname_format(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

        if value.lower() in [f.lower() for f in FORBIDDEN_NICKNAMES]:
            raise serializers.ValidationError("사용할 수 없는 닉네임입니다.")

        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    # 전화번호 검증
    def validate_phone_number(self, value: str) -> str:
        try:
            validate_phone_format(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)
        return value

    #### 비밀번호 검증 (Django 내장 validator 사용)
    def validate_password(self, value: str) -> str:
        #### Django 내장 validator 적용
        validate_password(value, user=self.instance)

        #### 커스텀 추가 규칙: 연속된 문자/숫자 3개 이상 체크
        for i in range(len(value) - 2):
            if value[i] == value[i + 1] == value[i + 2]:
                raise serializers.ValidationError(
                    "연속된 문자 또는 숫자를 3개 이상 사용할 수 없습니다."
                )

        #### 이메일 포함 여부 체크
        email = self.initial_data.get("email", "")
        if email and email.split("@")[0].lower() in value.lower():
            raise serializers.ValidationError(
                "이메일과 동일한 비밀번호는 사용할 수 없습니다."
            )

        return value

    #### 전체 검증
    def validate(self, data: dict) -> dict:
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "비밀번호가 일치하지 않습니다."}
            )

        #### 이메일 인증 확인
        email_info = TEMP_EMAIL_CODES.get(data["email"])
        if not email_info or email_info["code"] != data["email_code"]:
            raise serializers.ValidationError(
                {"email_code": "이메일 인증이 필요합니다."}
            )
        if email_info["expires"] < datetime.now():
            raise serializers.ValidationError(
                {"email_code": "인증코드가 만료되었습니다."}
            )

        #### 휴대폰 인증 확인
        phone_info = TEMP_PHONE_CODES.get(data["phone_number"])
        if not phone_info or phone_info["code"] != data["phone_code"]:
            raise serializers.ValidationError(
                {"phone_code": "휴대폰 인증이 필요합니다."}
            )
        if phone_info["expires"] < datetime.now():
            raise serializers.ValidationError(
                {"phone_code": "인증코드가 만료되었습니다."}
            )

        return data

    #### 유저 생성
    def create(self, validated_data: dict) -> Any:
        validated_data.pop("password_confirm")
        validated_data.pop("email_code")
        validated_data.pop("phone_code")
        user = User.objects.create_user(**validated_data)
        return user
