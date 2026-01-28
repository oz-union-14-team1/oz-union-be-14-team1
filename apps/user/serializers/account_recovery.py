from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class FindAccountSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        validate_password(data["new_password"])
        return data
