from django.test import TestCase
from apps.user.exceptions import RateLimitExceeded


class RateLimitExceededTestCase(TestCase):
    def test_exception_message_only(self):
        # 메시지만 있는 예외가 올바르게 초기화되는지 테스트
        message = "Rate limit exceeded"
        exc = RateLimitExceeded(message=message)

        self.assertEqual(exc.message, message)
        self.assertIsNone(exc.retry_after)
        self.assertEqual(str(exc), message)

    def test_exception_with_retry_after(self):
        # 메시지와 retry_after가 있는 예외가 올바르게 초기화 되는지 검증
        message = "Rate limit exceeded"
        retry_after = 60
        exc = RateLimitExceeded(message=message, retry_after=retry_after)

        self.assertEqual(exc.message, message)
        self.assertEqual(exc.retry_after, retry_after)
        self.assertEqual(str(exc), message)
