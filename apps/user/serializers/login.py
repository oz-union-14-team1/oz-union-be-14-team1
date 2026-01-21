from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 필수값 체크
        if not email:
            raise serializers.ValidationError({"email": ["이 필드는 필수 항목입니다."]})

        if not password:
            raise serializers.ValidationError(
                {"password": ["이 필드는 필수 항목입니다."]}
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "이메일 또는 비밀번호가 잘못되었습니다."},
            )

        # 탈퇴 계정 체크
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "탈퇴 신청한 계정입니다."},
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "이메일 또는 비밀번호가 잘못 되었습니다."},
            )

        attrs["user"] = user
        return attrs
