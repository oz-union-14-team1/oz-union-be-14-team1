from django.conf import settings

REFRESH_COOKIE_NAME = "refresh_token"


def set_refresh_cookie(response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        secure=settings.REFRESH_COOKIE_SECURE,
        path="/",
    )


def delete_refresh_cookie(response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/",
    )
