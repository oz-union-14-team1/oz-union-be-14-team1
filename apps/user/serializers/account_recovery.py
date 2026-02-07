import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.user.validators.validator import validate_phone_format


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


CODE_PURPOSE_CHOICES = (
    ("find_account", "아이디 찾기"),
    ("password_reset", "비밀번호 재설정"),
    ("update_phone", "휴대폰 변경/ 회원수정"),
)


class FindAccountSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=False, allow_blank=True)

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        validate_password(data["new_password"])
        return data


class CodeSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(
        choices=CODE_PURPOSE_CHOICES,
        default="password_reset",
        required=False,
    )

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized


class CodeVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(
        choices=CODE_PURPOSE_CHOICES,
        default="password_reset",
        required=False,
    )

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized

    def validate_code(self, value: str) -> str:
        value = (value or "").strip()
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("인증번호는 6자리 숫자여야 합니다.")
        return value
