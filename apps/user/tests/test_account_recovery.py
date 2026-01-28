from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.user.models import User


class AccountRecoveryAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="my_identifier_123",
            password="OldPassword1!",
            nickname="tester",
            name="테스터",
            phone_number="01012345678",
            gender="M",
        )

        self.user_id = self.user.id

        self.find_account_url = reverse("user:find_account")
        self.reset_request_url = reverse("user:password_reset_request")
        self.reset_confirm_url = reverse("user:password_reset_confirm")

    def test_find_account_success(self):
        res = self.client.post(
            self.find_account_url,
            {"identifier": "my_identifier_123", "phone_number": "01012345678"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["exists"])
        self.assertIn("nickname", res.data)
        self.assertIn("*", res.data["nickname"])

    def test_find_account_fail_wrong_phone(self):
        res = self.client.post(
            self.find_account_url,
            {"identifier": "my_identifier_123", "phone_number": "01000000000"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["exists"])

    def test_password_reset_request_creates_token_in_cache(self):
        res = self.client.post(
            self.reset_request_url,
            {"identifier": "my_identifier_123", "phone_number": "01012345678"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        token = self._extract_password_reset_token_from_cache()
        self.assertIsNotNone(token, "token이 cache에 저장되지 않았습니다.")

        cache_key = f"password_reset:{token}"
        user_id = cache.get(cache_key)
        self.assertEqual(user_id, self.user_id)

    def test_password_reset_confirm_success_changes_password_and_deletes_token(self):
        self.client.post(
            self.reset_request_url,
            {"identifier": "my_identifier_123", "phone_number": "01012345678"},
            format="json",
        )

        token = self._extract_password_reset_token_from_cache()
        self.assertIsNotNone(token)

        res = self.client.post(
            self.reset_confirm_url,
            {
                "token": token,
                "new_password": "NewPassword123!",
                "new_password_confirm": "NewPassword123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))

        self.assertIsNone(cache.get(f"password_reset:{token}"))

    def test_password_reset_confirm_invalid_token(self):
        res = self.client.post(
            self.reset_confirm_url,
            {
                "token": "invalid-token",
                "new_password": "NewPassword123!",
                "new_password_confirm": "NewPassword123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.data)

    def test_password_reset_confirm_password_mismatch(self):
        res = self.client.post(
            self.reset_confirm_url,
            {
                "token": "whatever",
                "new_password": "NewPassword123!",
                "new_password_confirm": "Different123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def _extract_password_reset_token_from_cache(self):
        internal = getattr(cache, "_cache", None)
        if isinstance(internal, dict):
            for k in internal.keys():
                if "password_reset:" in str(k):
                    return str(k).split("password_reset:")[-1]
            return None
        return None
