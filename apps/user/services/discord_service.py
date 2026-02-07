import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class DiscordLoginService:
    # 디스코드 OAuth2 엔드포인트
    TOKEN_URI = "https://discord.com/api/oauth2/token"
    USER_INFO_URI = "https://discord.com/api/users/@me"

    def __init__(self, redirect_uri):
        self.client_id = settings.DISCORD_CLIENT_ID
        self.client_secret = settings.DISCORD_CLIENT_SECRET
        self.redirect_uri = redirect_uri

    def get_access_token(self, code):
        """
        디스코드 인증 코드를 사용해 Access Token을 요청합니다.
        Content-Type: application/x-www-form-urlencoded
        """
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.TOKEN_URI, data=payload, headers=headers)

        if not response.ok:
            raise ValidationError(f"디스코드 토큰 발급 실패: {response.text}")

        return response.json().get("access_token")

    def get_user_info(self, access_token):
        """
        Access Token으로 유저 정보를 가져옵니다.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URI, headers=headers)

        if not response.ok:
            raise ValidationError("디스코드 유저 정보 조회 실패")

        return response.json()