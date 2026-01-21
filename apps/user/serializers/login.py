from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()

LOGIN_FAILED_MESSAGE = "이메일 또는 비밀번호가 올바르지 않습니다."


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 이메일 존재 여부 노출 방지
            raise serializers.ValidationError({"detail": LOGIN_FAILED_MESSAGE})

        # 탈퇴(비활성) 계정
        if not user.is_active:
            raise PermissionDenied("탈퇴 신청한 계정입니다.")

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": LOGIN_FAILED_MESSAGE})

        attrs["user"] = user
        return attrs
