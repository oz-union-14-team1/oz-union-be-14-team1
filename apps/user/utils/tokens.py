from __future__ import annotations

import secrets
import time
from typing import Optional

from django.core.cache import caches
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.user.utils.verification import TOKEN_BYTES, DEFAULT_TTL_SECONDS


class TokenService:
    def __init__(
        self, redis_alias: str = "default", namespace: str = "auth_token"
    ) -> None:
        self.cache = caches[redis_alias]
        self.namespace = namespace

    # Redis에 실제로 저장할 키 생성
    def _key(self, token: str) -> str:
        return f"{self.namespace}:{token}"

    # 토큰 발급
    def generate(self, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
        token = secrets.token_urlsafe(TOKEN_BYTES)
        self.cache.set(self._key(token), value, timeout=ttl_seconds)
        return token

    # 토큰 검증
    def verify(self, token: str, *, consume: bool = True) -> Optional[str]:
        key = self._key(token)
        value = self.cache.get(key)
        if value is None:
            return None
        if consume:
            self.cache.delete(key)
        return value

    # 토큰 강제 삭제
    def revoke(self, token: str) -> None:
        self.cache.delete(self._key(token))

    # JWT pair 발급
    def create_token_pair(self, *, user) -> tuple[str, str]:
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        return str(refresh_token), access_token

    def _blacklist_key(self, refresh_token: str) -> str:
        return f"{self.namespace}:bl:{refresh_token}"

    def blacklist(self, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)  # type: ignore[arg-type]
            exp = int(token["exp"])
        except (TypeError, KeyError, ValueError, TokenError):
            return

        ttl = max(exp - int(time.time()), 0)
        if ttl <= 0:
            return

        self.cache.set(self._blacklist_key(refresh_token), "1", timeout=ttl)

    def is_refresh_blacklisted(self, refresh_token: str) -> bool:
        return self.cache.get(self._blacklist_key(refresh_token)) is not None

    def refresh_access_token(self, refresh_token: str) -> str:
        if self.is_refresh_blacklisted(refresh_token):
            raise TokenError("refresh token이 블랙리스트 됐습니다.")

        token = RefreshToken(refresh_token)  # type: ignore[arg-type]
        return str(token.access_token)

    def _access_blacklist_key(self, jti: str) -> str:
        return f"{self.namespace}:abl:{jti}"

    def blacklist_access(self, access_token: str) -> None:
        try:
            token = AccessToken(access_token)  # type: ignore[arg-type]
            exp = int(token["exp"])
            jti = str(token["jti"])
        except (TypeError, KeyError, ValueError, TokenError):
            return

        ttl = max(exp - int(time.time()), 0)
        if ttl <= 0:
            return

        self.cache.set(self._access_blacklist_key(jti), "1", timeout=ttl)

    def is_access_blacklisted(self, access_token: str) -> bool:
        try:
            token = AccessToken(access_token)  # type: ignore[arg-type]
            jti = str(token["jti"])
        except (TypeError, KeyError, ValueError, TokenError):
            return False

        return self.cache.get(self._access_blacklist_key(jti)) is not None
