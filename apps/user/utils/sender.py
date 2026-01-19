import telnyx  # type: ignore[import-not-found]
from django.conf import settings

# Tenlyx에 내 API키로 인증
telnyx.api_key = settings.TELNYX_API_KEY  # type: ignore[attr-defined]


class SMSSender:
    @staticmethod
    def send_verification_code(phone: str, code: str) -> None:  # SMS 보내는 함수 정의
        body = f"PlayType 인증 코드: {code}"

        telnyx.Message.create(  # type: ignore[attr-defined]
            from_=settings.TELNYX_FROM_NUMBER,
            to=phone,
            text=body,
        )
