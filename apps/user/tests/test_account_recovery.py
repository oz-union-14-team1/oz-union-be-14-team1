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

        cache.clear()

    def test_find_account_success(self):
        res = self.client.post(
            self.find_account_url,
            {"phone_number": "01012345678"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["exists"])
        self.assertIn("identifier", res.data)
        self.assertIn("*", res.data["identifier"])
        self.assertIn("message", res.data)

    def test_find_account_fail_wrong_phone(self):
        res = self.client.post(
            self.find_account_url,
            {"phone_number": "01000000000"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["exists"])
        self.assertIn("message", res.data)

    def test_password_reset_request_creates_code_in_cache(self):
        res = self.client.post(
            self.reset_request_url,
            {"identifier": "my_identifier_123", "phone_number": "01012345678"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        code = self._extract_password_reset_code_from_cache()
        self.assertIsNotNone(code, "6자리 code가 cache에 저장되지 않았습니다.")

        cache_key = f"password_reset:{code}"
        user_id = cache.get(cache_key)
        self.assertEqual(user_id, self.user_id)

    def test_password_reset_confirm_success_changes_password_and_deletes_code(self):
        self.client.post(
            self.reset_request_url,
            {"identifier": "my_identifier_123", "phone_number": "01012345678"},
            format="json",
        )

        code = self._extract_password_reset_code_from_cache()
        self.assertIsNotNone(code)

        res = self.client.post(
            self.reset_confirm_url,
            {
                "code": code,
                "new_password": "NewPassword123!",
                "new_password_confirm": "NewPassword123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))

        self.assertIsNone(cache.get(f"password_reset:{code}"))  # 수정됨

    def test_password_reset_confirm_invalid_code(self):
        res = self.client.post(
            self.reset_confirm_url,
            {
                "code": "000000",
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
                "code": "123456",
                "new_password": "NewPassword123!",
                "new_password_confirm": "Different123!",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def _extract_password_reset_code_from_cache(self):
        internal = getattr(cache, "_cache", None)
        if isinstance(internal, dict):
            for k in internal.keys():
                s = str(k)
                if "password_reset:" in s:
                    return s.split("password_reset:")[-1]
            return None
        return None
