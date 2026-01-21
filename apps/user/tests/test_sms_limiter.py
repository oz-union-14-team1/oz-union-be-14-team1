from django.test import TestCase
from unittest.mock import MagicMock
from apps.user.constants.period import Period
from apps.user.exceptions import RateLimitExceeded
from apps.user.utils.limiter import SMSLimiter


class SMSLimiterTestCase(TestCase):
    def setUp(self):
        # 공통 설정
        self.mock_redis = MagicMock()
        self.limiter = SMSLimiter()
        self.limiter.redis = self.mock_redis
        self.phone = "01012345678"
        self.limit = 3
        self.ttl = 60

    def test_key_generation(self):
        # _key 메서드가 올바른 Redis 키 문자열을 생성하는지에 대한 테스트
        key = self.limiter._key(self.phone, Period.MINUTE)
        expected_key = f"{self.limiter.namespace}:{Period.MINUTE.value}:{self.phone}"
        self.assertEqual(key, expected_key)

    def test_can_send_under_limit(self):
        # sms 발송 횟수 제한 이하 일때 can_send가 True를 반환 하는지 테스트
        self.mock_redis.get.return_value = 2
        can_send = self.limiter.can_send(self.phone, Period.MINUTE, self.limit)
        self.assertTrue(can_send)

    def test_can_send_over_limit(self):
        # sms 발송 횟수가 제한 이상 일때 can_send가 False를 반환하는지 테스트
        self.mock_redis.get.return_value = 3
        can_send = self.limiter.can_send(self.phone, Period.MINUTE, self.limit)
        self.assertFalse(can_send)

    def test_record_increment_and_ttl_set(self):
        # record 호출시 Redis incr 와 expire가 올바르게 호출하면서 True가 반환되는지 테스트
        self.mock_redis.incr.return_value = 1
        self.mock_redis.expire = MagicMock()

        result = self.limiter.record(self.phone, Period.MINUTE, self.limit, self.ttl)
        self.mock_redis.incr.assert_called_once()
        self.mock_redis.expire.assert_called_once_with(
            f"{self.limiter.namespace}:{Period.MINUTE.value}:{self.phone}", self.ttl
        )
        self.assertTrue(result)

    def test_record_exceed_limit_raises_exception(self):
        # SMS 발송 한도 초과 테스트
        self.mock_redis.incr.return_value = self.limit + 1
        self.mock_redis.ttl.return_value = 30  # 남은 시간 설정

        with self.assertRaises(RateLimitExceeded) as context:
            self.limiter.record(self.phone, Period.MINUTE, self.limit, self.ttl)

        self.assertIn("SMS 발송 한도를 초과했습니다", str(context.exception))
        self.assertEqual(context.exception.retry_after, 30)

    def test_get_remaining_returns_ttl(self):
        # get_remaining 부르면 Redis TTL를 제대로 반환하는지 검증
        self.mock_redis.ttl.return_value = 45
        remaining = self.limiter.get_remaining(self.phone, Period.MINUTE)
        self.assertEqual(remaining, 45)

    def test_get_remaining_returns_none_if_no_ttl(self):
        # get_remaining가 없으면 Redis TTL를 제대로 None 반환하는지 검증
        self.mock_redis.ttl = None
        remaining = self.limiter.get_remaining(self.phone, Period.MINUTE)
        self.assertIsNone(remaining)
