from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.user.utils.tokens import TokenService
import re

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    email_token = serializers.CharField(required=True)
    sms_token = serializers.CharField(required=True)

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
        extra_kwargs = {
            "password": {"write_only": True},
            "nickname": {"write_only": True},
            "name": {"write_only": True},
            "gender": {"write_only": True},
        }

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

        # 연속된 문자/ 숫자 3개 이상 검사
        for i in range(len(value) - 2):
            if (
                ord(value[i + 1]) == ord(value[i]) + 1
                and ord(value[i + 2]) == ord(value[i]) + 2
            ):
                raise serializers.ValidationError(
                    "연속된 문자/ 숫자를 3개 이상 사용할 수 없습니다."
                )

        # 이메일과 동일 불가
        email_token = getattr(self, "initial_data", {}).get("email_token")
        if email_token and email_token in value:
            raise serializers.ValidationError("비밀번호에 이메일을 포함할 수 없습니다.")

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
        """email_token, sms_token 검증 및 중복 체크"""
        token_service = TokenService()
        email_value = token_service.verify(attrs.get("email_token"))
        if email_value is None:
            raise serializers.ValidationError(
                {"email_token": ["유효하지 않거나 만료된 토큰입니다."]}
            )
        attrs["email"] = email_value

        phone_value = token_service.verify(attrs.get("sms_token"))
        if phone_value is None:
            raise serializers.ValidationError(
                {"sms_token": ["유효하지 않거나 만료된 토큰입니다."]}
            )
        attrs["phone_number"] = phone_value

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
        email = validated_data.pop("email")  # 수정됨
        phone = validated_data.pop("phone_number")  # 수정됨

        validated_data.pop("email_token", None)  # 수정됨
        validated_data.pop("sms_token", None)  # 수정됨

        user = User.objects.create_user(
            email=email,
            phone_number=phone,
            password=validated_data["password"],
            name=validated_data["name"],
            nickname=validated_data["nickname"],
            gender=validated_data["gender"],
        )

        return user
