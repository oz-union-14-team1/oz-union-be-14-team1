from __future__ import annotations

import secrets
from typing import Optional
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.cache import caches

from apps.user.constants.time import ACCESS_TOKEN_EXPIRE_SECONDS
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

    def create_access_token(self, *, user) -> str:
        now = datetime.utcnow()

        payload = {
            "user_id": user.id,
            "email": user.email,
            "iat": now,
            "exp": now + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )
