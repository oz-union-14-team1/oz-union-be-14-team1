from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.user.utils.tokens import TokenService


class BlacklistJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, validated_token = result

        # raw access token 문자열 뽑기
        header = self.get_header(request)
        if header is None:
            return result

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return result

        access_str = (
            raw_token.decode()
            if isinstance(raw_token, (bytes, bytearray))
            else str(raw_token)
        )

        if TokenService().is_access_blacklisted(access_str):
            raise AuthenticationFailed(
                "로그아웃된 토큰입니다.", code="token_blacklisted"
            )

        return (user, validated_token)
