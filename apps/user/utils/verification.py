from __future__ import annotations
import secrets
from typing import Optional, cast

from django.conf import settings
from django.core.cache import caches

CODE_LENGTH = cast(int, settings.VERIFICATION_CODE_LENGTH)
TOKEN_BYTES = cast(int, settings.VERIFICATION_TOKEN_BYTES)
CODE_CHARS: str = settings.VERIFICATION_CODE_CHARS
DEFAULT_TTL_SECONDS = cast(int, settings.VERIFICATION_DEFAULT_TTL_SECONDS)
TOKEN_GENERATE_MAX_ATTEMPTS = cast(
    int, settings.VERIFICATION_TOKEN_GENERATE_MAX_ATTEMPTS
)


def _normalize(identifier: str) -> str:
    return identifier.strip()


class SMSVerificationsService:
    def __init__(
        self, redis_alias: str = "default", namespace: str = "sms_verification"
    ) -> None:
        self.redis = caches[redis_alias]
        self.namespace = namespace

    # Redis 키 생성
    def _code_key(self, phone: str) -> str:
        return f"{self.namespace}:code:{phone}"

    def _token_key(self, token: str) -> str:
        return f"{self.namespace}:token:{token}"

    # 코드 생성
    def generate_code(self, phone: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
        phone = _normalize(phone)
        code = "".join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
        self.redis.set(self._code_key(phone), code, ttl_seconds)
        return code

    # 코드 검증
    def verify_code(self, phone: str, code: str, consume: bool = True) -> bool:
        phone = _normalize(phone)
        key = self._code_key(phone)
        stored = self.redis.get(key)

        if stored is None:
            return False

        stored_code = (
            stored.decode() if isinstance(stored, (bytes, bytearray)) else stored
        )

        if stored_code != code:
            return False

        if consume:
            self.redis.delete(key)

        return True

    # 1회용 토큰 생성
    def generate_token(self, phone: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
        phone = _normalize(phone)

        for _ in range(TOKEN_GENERATE_MAX_ATTEMPTS):
            token = secrets.token_urlsafe(TOKEN_BYTES)
            key = self._token_key(token)
            if not self.redis.get(key):
                self.redis.set(key, phone, ttl_seconds)
                return token

        raise RuntimeError("Token generation failed")

    # 토큰 검증
    def verify_token(self, token: str, consume: bool = True) -> Optional[str]:
        key = self._token_key(token)
        value = self.redis.get(key)

        if value is None:
            return None

        phone = value.decode() if isinstance(value, (bytes, bytearray)) else value

        if consume:
            self.redis.delete(key)

        return phone

    # 남은 TTL 조회
    def get_remaining_ttl(
        self, identifier_or_token: str, *, is_token: bool = False
    ) -> Optional[int]:
        key = (
            self._token_key(identifier_or_token)
            if is_token
            else self._token_key(_normalize(identifier_or_token))
        )
        ttl_func = getattr(self.redis, "ttl", None)
        if ttl_func is None:
            return None

        remaining = ttl_func(key)
        return remaining if remaining and remaining > 0 else None

    # 강제 삭제
    def clear(self, identifier_or_token: str, *, is_token: bool = False) -> None:
        key = (
            self._token_key(identifier_or_token)
            if is_token
            else self._token_key(_normalize(identifier_or_token))
        )
        self.redis.delete(key)
