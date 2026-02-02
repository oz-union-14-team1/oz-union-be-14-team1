from __future__ import annotations

import secrets
import time
from typing import Optional
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.core.cache import caches

from apps.user.utils.verification import TOKEN_BYTES, DEFAULT_TTL_SECONDS


class TokenService:
    def __init__(
        self, redis_alias: str = "default", namespace: str = "auth_token"
    ) -> None:

        # redis 캐시 객체
        self.cache = caches[redis_alias]

        # redis key 앞에 붙을 네임스페이스
        self.namespace = namespace

    # 내부용: Redis에 실제로 저장할 키 생성
    def _key(self, token: str) -> str:
        return f"{self.namespace}:{token}"

    # 토큰 발급
    def generate(self, value: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
        # 랜덤 토큰 생성
        token = secrets.token_urlsafe(TOKEN_BYTES)
        self.cache.set(self._key(token), value, timeout=ttl_seconds)
        return token

    # 토큰이 유효한지에 대해서 검증
    def verify(self, token: str, *, consume: bool = True) -> Optional[str]:
        key = self._key(token)

        # redis에서 값을 조회
        value = self.cache.get(key)
        # 토큰이 없어 or 만료됐어
        if value is None:
            return None

        # 1회용이면 삭제
        if consume:
            self.cache.delete(key)
        return value

    # 토큰 강제 삭제
    def revoke(self, token: str) -> None:
        self.cache.delete(self._key(token))

    def create_token_pair(self, *, user) -> tuple[str, str]:
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        return str(refresh_token), access_token
    # 토큰 재발급
    def _bl_key(self, refresh_token: str) -> str:
        return f"{self.namespace}:bl:{refresh_token}"

    # 토큰 블랙리스트
    def black_list(self, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            exp = int(token["exp"])
        except (TypeError, KeyError, ValueError, TokenError):
            return

        now = int(time.time())
        ttl = max(exp - now, 0)
        if ttl <= 0:
            return

        self.cache.set(self._bl_key(refresh_token), "1", timeout=ttl)

    def is_refresh_blacklisted(self, refresh_token: str) -> bool:
        return self.cache.get(self._bl_key(refresh_token)) is not None