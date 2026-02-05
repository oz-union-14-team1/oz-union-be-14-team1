import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class EmailAvailabilitySerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        value = (value or "").strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value


class NicknameAvailabilitySerializer(serializers.Serializer):
    nickname = serializers.CharField()

    def validate_nickname(self, value: str) -> str:
        value = (value or "").strip()

        if len(value) < 2 or len(value) > 16:
            raise serializers.ValidationError("닉네임은 2~16자여야 합니다.")
        if not re.search(r"^[a-zA-Z0-9가-힣]+$", value):
            raise serializers.ValidationError("닉네임은 한글, 영문, 숫자만 가능합니다.")

        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and getattr(user, "is_authenticated", False):
            if value == (user.nickname or ""):
                raise serializers.ValidationError("기존 닉네임과 동일합니다.")

            if User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
                raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
            return value

        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value
