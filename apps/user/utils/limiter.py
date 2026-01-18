from __future__ import annotations
from typing import Optional

from django.core.cache import caches
from django.core.cache.backends.base import BaseCache

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24


class SMSLimiter:
    def __init__(self, redis_alias: str = "default", namespace: str = "limiter_sms"):
        self.cache: BaseCache = caches[redis_alias]
        self.namespace = namespace

    # Redis key 생성
    def _key(self, phone: str, period: str) -> str:
        phone_normalized = phone.strip()
        return f"{self.namespace}:{period}:{phone_normalized}"

    # 이번요청이 허용되는지 확인
    def can_send(self, phone: str, period: str, limit: int) -> bool:
        key = self._key(phone, period)
        count = self.redis.get(key) or 0
        return int(count) < limit

    # 요청기록 + 카운트 증가 Redis에 키가 없으면 생성 TTL 설정 , Redis에 키가 있으면 incr만 함
    def record(self, phone: str, period: str, limit: int, ttl: str) -> bool:
        key = self._key(phone, period)
        new = self.redis.incr(key)

        if new == 1:
            self.redis.expire(key, ttl)

        return new <= limit

    # 남은 TTL 조회 (초 단위로 조회)
    def get_remaining(self, phone: str, period: str) -> Optional[int]:
        key = self._key(phone, period)
        ttl_func = getattr(self.redis, "ttl", None)
        if ttl_func is None:
            return None
        return ttl_func(key)
