from django.test import TestCase
from unittest.mock import MagicMock, patch
from ..utils.tokens import TokenService, DEFAULT_TTL_SECONDS


class TokenServiceTestCase(TestCase):
    def setUp(self):
        self.mock_cache = MagicMock()
        self.service = TokenService()
        self.service.cache = self.mock_cache

        self.value = "test_user"
        self.ttl = DEFAULT_TTL_SECONDS

    def test_key_generation(self):
        token = "abcd1234"
        key = self.service._key(token)
        self.assertEqual(key, f"{self.service.namespace}:{token}")

    @patch("secrets.token_urlsafe", return_value="randomtoken")
    def test_generate_stores_token_in_cache(self, mock_token):
        token = self.service.generate(self.value, ttl_seconds=self.ttl)

        self.assertEqual(token, "randomtoken")
        self.mock_cache.set.assert_called_once_with(
            f"{self.service.namespace}:{token}", self.value, timeout=self.ttl
        )

    def test_verify_returns_value_and_consumes_token(self):
        token = "abcd1234"
        key = self.service._key(token)
        self.mock_cache.get.return_value = self.value

        result = self.service.verify(token, consume=True)

        self.assertEqual(result, self.value)
        self.mock_cache.delete.assert_called_once_with(key)

    def test_verify_returns_value_without_consuming(self):
        token = "abcd1234"
        self.mock_cache.get.return_value = self.value

        result = self.service.verify(token, consume=False)

        self.assertEqual(result, self.value)
        self.mock_cache.delete.assert_not_called()

    def test_verify_returns_none_if_token_missing(self):
        token = "missingtoken"
        self.mock_cache.get.return_value = None

        result = self.service.verify(token)
        self.assertIsNone(result)

    def test_revoke_deletes_token(self):
        token = "abcd1234"
        key = self.service._key(token)

        self.service.revoke(token)
        self.mock_cache.delete.assert_called_once_with(key)
