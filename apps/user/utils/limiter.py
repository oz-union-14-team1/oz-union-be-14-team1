from __future__ import annotations
from typing import Optional, Any

from django.core.cache import caches

from apps.user.exceptions import RateLimitExceeded
from apps.user.constants import Period


class SMSLimiter:
    def __init__(self, redis_alias: str = "default", namespace: str = "limiter_sms"):
        self.redis: Any = caches[redis_alias]
        self.namespace = namespace

    # Redis key 생성
    def _key(self, phone: str, period: Period) -> str:
        phone_normalized = phone.strip()
        return f"{self.namespace}:{period.value}:{phone_normalized}"

    # 이번요청이 허용되는지 확인
    def can_send(self, phone: str, period: Period, limit: int) -> bool:
        key = self._key(phone, period)
        count = self.redis.get(key) or 0
        return int(count) < limit

    # 요청기록 + 제한 확인 기록 후에 카운트증가 ( Redis에 키가 없으면 생성 TTL 설정 , Redis에 키가 있으면 incr만 함)
    def record(self, phone: str, period: Period, limit: int, ttl: int) -> bool:
        try:
            key = self._key(phone, period)
            new = self.redis.incr(key)

            if new == 1:  # 처음 생성
                self.redis.expire(key, ttl)

            if new > limit:  # 제한 초과 시
                retry_after = self.get_remaining(phone, period)
                raise RateLimitExceeded(
                    message=f"SMS 발송 한도를 초과했습니다. {retry_after}초 후에 다시 시도해주세요.",
                    retry_after=retry_after,
                )
            return True

        except RateLimitExceeded:
            raise
        except Exception as e:
            raise Exception(f"SMS 발송 기록 중 오류 발생: {str(e)}")

    # 남은 TTL 조회 (초 단위로 조회)
    def get_remaining(self, phone: str, period: Period) -> Optional[int]:
        key = self._key(phone, period)
        ttl_func = getattr(self.redis, "ttl", None)
        if ttl_func is None:
            return None
        return ttl_func(key)
