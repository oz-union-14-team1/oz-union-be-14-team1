from rest_framework import serializers


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        help_text="로그인 시 발급받은 refresh token"
    )
