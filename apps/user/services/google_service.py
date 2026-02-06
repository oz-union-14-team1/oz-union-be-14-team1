import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class GoogleLoginService:
    TOKEN_URI = "https://oauth2.googleapis.com/token"
    USER_INFO_URI = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, redirect_uri):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = redirect_uri

    def get_access_token(self, code):
        """
        1. 프론트에서 받은 'code'를 가지고 구글에게 'Access Token'을 달라고 요청합니다.
        """
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.TOKEN_URI, data=payload)

        if not response.ok:
            raise ValidationError(f"구글 토큰 발급 실패: {response.text}")

        return response.json().get("access_token")

    def get_user_info(self, access_token):
        """
        2. 받은 'Access Token'으로 유저의 이메일 등 정보를 가져옵니다.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.USER_INFO_URI, headers=headers)

        if not response.ok:
            raise ValidationError("구글 유저 정보 조회 실패")

        return response.json()
