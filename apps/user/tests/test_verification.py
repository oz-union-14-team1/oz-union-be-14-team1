from django.test import TestCase
from unittest.mock import MagicMock, patch
from ..utils.verification import SMSVerificationsService, DEFAULT_TTL_SECONDS  # 수정됨


class SMSVerificationsServiceTestCase(TestCase):
    def setUp(self):
        self.mock_cache = MagicMock()
        self.service = SMSVerificationsService()  # 수정됨
        self.service.redis = self.mock_cache  # 수정됨

        self.phone = "01012345678"
        self.code = "123456"
        self.token = "token123"
        self.ttl = DEFAULT_TTL_SECONDS

    # 코드 키 생성
    def test_code_key_generation(self):
        key = self.service._code_key(self.phone)
        self.assertEqual(key, f"{self.service.namespace}:code:{self.phone}")

    # 토큰 키 생성
    def test_token_key_generation(self):
        key = self.service._token_key(self.token)
        self.assertEqual(key, f"{self.service.namespace}:token:{self.token}")

    # 코드 생성 테스트
    @patch("secrets.choice", side_effect=list("123456"))  # 코드 생성 랜덤값 mock
    def test_generate_code_stores_in_cache(self, mock_choice):
        code = self.service.generate_code(self.phone, ttl_seconds=self.ttl)
        self.assertEqual(code, "123456")
        self.mock_cache.set.assert_called_once_with(
            self.service._code_key(self.phone), code, self.ttl
        )

    # 코드 검증 성공 + consume=True
    def test_verify_code_success_and_consume(self):
        self.mock_cache.get.return_value = self.code
        result = self.service.verify_code(self.phone, self.code, consume=True)
        self.assertTrue(result)
        self.mock_cache.delete.assert_called_once_with(
            self.service._code_key(self.phone)
        )

    # 코드 검증 성공 + consume=False
    def test_verify_code_success_without_consume(self):
        self.mock_cache.get.return_value = self.code
        result = self.service.verify_code(self.phone, self.code, consume=False)
        self.assertTrue(result)
        self.mock_cache.delete.assert_not_called()

    # 코드 검증 실패 (잘못된 코드)
    def test_verify_code_failure_wrong_code(self):
        self.mock_cache.get.return_value = self.code
        result = self.service.verify_code(self.phone, "wrongcode")
        self.assertFalse(result)

    # 코드 검증 실패 (없음)
    def test_verify_code_failure_missing(self):
        self.mock_cache.get.return_value = None
        result = self.service.verify_code(self.phone, self.code)
        self.assertFalse(result)

    # 토큰 생성 테스트
    @patch("secrets.token_urlsafe", return_value="randomtoken")
    def test_generate_token_stores_in_cache(self, mock_token):
        self.mock_cache.get.return_value = None  # 수정됨: Redis에 키 없다고 가정
        token = self.service.generate_token(self.phone, ttl_seconds=self.ttl)
        self.assertEqual(token, "randomtoken")
        self.mock_cache.set.assert_called_once_with(
            self.service._token_key(token), self.phone, self.ttl
        )

    # 토큰 검증 성공 + consume=True
    def test_verify_token_success_and_consume(self):
        self.mock_cache.get.return_value = self.phone
        result = self.service.verify_token(self.token, consume=True)
        self.assertEqual(result, self.phone)
        self.mock_cache.delete.assert_called_once_with(
            self.service._token_key(self.token)
        )

    # 토큰 검증 성공 + consume=False
    def test_verify_token_success_without_consume(self):
        self.mock_cache.get.return_value = self.phone
        result = self.service.verify_token(self.token, consume=False)
        self.assertEqual(result, self.phone)
        self.mock_cache.delete.assert_not_called()

    # 토큰 검증 실패
    def test_verify_token_failure_missing(self):
        self.mock_cache.get.return_value = None
        result = self.service.verify_token(self.token)
        self.assertIsNone(result)

    # 강제 삭제
    def test_clear_removes_code_or_token(self):
        self.service.clear(self.phone)  # 코드 삭제
        self.mock_cache.delete.assert_called_with(self.service._token_key(self.phone))
        self.mock_cache.delete.reset_mock()
        self.service.clear(self.token, is_token=True)  # 토큰 삭제
        self.mock_cache.delete.assert_called_with(self.service._token_key(self.token))

    # TTL 조회 정상
    def test_get_remaining_ttl_returns_value(self):
        self.mock_cache.ttl.return_value = 120
        remaining = self.service.get_remaining_ttl(self.token, is_token=True)
        self.assertEqual(remaining, 120)

    # TTL 조회 없음 또는 만료
    def test_get_remaining_ttl_returns_none_if_missing_or_expired(self):
        self.mock_cache.ttl.return_value = None
        remaining = self.service.get_remaining_ttl(self.token, is_token=True)
        self.assertIsNone(remaining)
        self.mock_cache.ttl.return_value = 0
        remaining = self.service.get_remaining_ttl(self.token, is_token=True)
        self.assertIsNone(remaining)
