from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

from apps.user.validators.validator import validate_phone_format

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField()
    name = serializers.CharField()
    gender = serializers.ChoiceField(choices=("M", "F"))
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "nickname",
            "name",
            "gender",
            "phone_number",
        ]

    def validate_email(self, value: str) -> str:
        value = (value or "").strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return value

    def validate_password(self, value: str) -> str:
        """비밀번호 유효성 검증"""
        if len(value) < 8 or len(value) > 20:
            raise serializers.ValidationError("비밀번호는 8~20자여야 합니다.")

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("대문자를 최소 1개 포함해야 합니다.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("소문자를 최소 1개 포함해야 합니다.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("숫자를 최소 1개 포함해야 합니다.")
        if not re.search(r"[!@#$%^&*]", value):
            raise serializers.ValidationError("특수문자를 최소 1개 포함해야 합니다.")
        return value

    def validate_nickname(self, value: str) -> str:
        """닉네임 유효성 검사 중복 검사"""
        if len(value) < 2 or len(value) > 16:
            raise serializers.ValidationError("닉네임은 2~16자여야 합니다.")
        if not re.search(r"^[a-zA-Z0-9가-힣]+$", value):
            raise serializers.ValidationError("닉네임은 한글, 영문, 숫자만 가능합니다.")
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

    def validate_phone_number(self, value: str) -> str:
        normalized = re.sub(r"\D", "", value or "")
        validate_phone_format(normalized)

        if User.objects.filter(phone_number=normalized, is_active=True).exists():
            raise serializers.ValidationError("이미 가입된 휴대폰 번호입니다.")

        return normalized

    def create(self, validated_data):
        email = validated_data.pop("email")

        user = User.objects.create_user(
            email=email,
            password=validated_data["password"],
            name=validated_data["name"],
            nickname=validated_data["nickname"],
            gender=validated_data["gender"],
            phone_number=validated_data["phone_number"],
        )

        return user


class RegisterResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
