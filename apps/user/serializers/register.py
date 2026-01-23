from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.user.utils.tokens import TokenService
import re

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField()
    name = serializers.CharField()
    gender = serializers.ChoiceField(choices=("M", "F"))

    class Meta:
        model = User
        fields = [
            "password",
            "nickname",
            "name",
            "email_token",
            "sms_token",
            "gender",
        ]

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

    def validate(self, attrs):
        # 이메일/ 전화번호 중복 체크
        email = attrs.get("email")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": ["이미 가입된 이메일입니다."]})
        if User.objects.filter(phone_number=attrs["phone_number"]).exists():
            raise serializers.ValidationError(
                {"phone_number": ["이미 가입된 번호입니다."]}
            )

        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email")
        phone = validated_data.pop("phone_number")

        validated_data.pop("email_token", None)
        validated_data.pop("sms_token", None)

        user = User.objects.create_user(
            email=email,
            phone_number=phone,
            password=validated_data["password"],
            name=validated_data["name"],
            nickname=validated_data["nickname"],
            gender=validated_data["gender"],
        )

        return user

class RegisterResponseSerializer(serializers.Serializer):
    detail=serializers.CharField()
    access_token=serializers.CharField()