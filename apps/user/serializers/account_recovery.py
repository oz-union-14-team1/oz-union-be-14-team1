import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.user.validators.validator import validate_phone_format


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


class FindAccountSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value: str) -> str:
        normalized = normalize_phone(value)
        validate_phone_format(normalized)
        return normalized


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        validate_password(data["new_password"])
        return data
