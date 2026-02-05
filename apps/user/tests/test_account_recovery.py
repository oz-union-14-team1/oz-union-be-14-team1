from __future__ import annotations

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.user.models import User
from apps.user.views.account_recovery import _generate_6bigit_code, _mask, mask_email


@override_settings(
    VERIFICATION_DEFAULT_TTL_SECONDS=300,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    },
)
class AccountRecoveryAPITest(APITestCase):
    """
    account_recovery.py 뷰/헬퍼 기준 커버리지 올리는 최종본.
    - FindAccount: verify:ok:find_account:{phone} 필요
    - CodeSend: DEBUG True/False 분기
    - CodeVerify: saved_code 없음 / 불일치 / 성공 분기
    - PasswordResetRequest: ok 없음 / code 불일치 / user 없음 / 성공 분기
    - PasswordResetConfirm: 쿠키 없음 / 토큰 invalid / user inactive / 성공 분기
    """

    def setUp(self):
        cache.clear()

        self.code_send_url = reverse("user:code_send")
        self.code_verify_url = reverse("user:code_verify")
        self.find_account_url = reverse("user:find_account")
        self.reset_request_url = reverse("user:password_reset_request")
        self.reset_confirm_url = reverse("user:password_reset_confirm")

        self.phone = "01012345678"
        self.email = "testtesttest@example.com"
        self.password = "OldPassword1!"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            nickname="tester",
            name="테스터",
            phone_number=self.phone,
            gender="M",
            is_active=True,
        )

    # -----------------------------
    # Helpers (unit)
    # -----------------------------
    def test_helpers__mask_branches(self):
        # len <= 1
        self.assertEqual(_mask(""), "*")
        self.assertEqual(_mask("a"), "a*")
        # len == 2
        self.assertEqual(_mask("ab"), "a*")
        # len == 3
        self.assertEqual(_mask("abc"), "a*c")
        # len >= 4
        self.assertEqual(_mask("abcd"), "abcd")  # (len-4)=0
        self.assertEqual(_mask("abcde"), "ab*de")  # 1개 마스크
        self.assertEqual(_mask("abcdef"), "ab**ef")  # 2개 마스크

    def test_helpers_mask_email_branches(self):
        # '@' 없음
        self.assertEqual(mask_email("abc"), "a*c")
        # '@' 있음: local만 마스킹
        self.assertEqual(mask_email("a@example.com"), "a*@example.com")
        self.assertEqual(mask_email("abc@example.com"), "a*c@example.com")
        self.assertEqual(mask_email("abcdef@example.com"), "ab**ef@example.com")

    def test_helpers_generate_6digit_code(self):
        code = _generate_6bigit_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    # -----------------------------
    # CodeSendView
    # -----------------------------
    @override_settings(DEBUG=True)
    def test_code_send_debug_true_returns_code_and_sets_cache(self):
        res = self.client.post(
            self.code_send_url,
            {"phone_number": self.phone, "purpose": "password_reset"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "인증번호를 전송했습니다.")
        self.assertIn("code", res.data)

        code = res.data["code"]
        saved = cache.get(f"verify:sms:password_reset:{self.phone}")
        self.assertEqual(saved, code)

    @override_settings(DEBUG=False)
    def test_code_send_debug_false_does_not_return_code_but_sets_cache(self):
        res = self.client.post(
            self.code_send_url,
            {"phone_number": self.phone, "purpose": "password_reset"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "인증번호를 전송했습니다.")
        self.assertNotIn("code", res.data)  # ✅ DEBUG=False 분기

        saved = cache.get(f"verify:sms:password_reset:{self.phone}")
        self.assertIsNotNone(saved)
        self.assertEqual(len(str(saved)), 6)
        self.assertTrue(str(saved).isdigit())

    # -----------------------------
    # CodeVerifyView
    # -----------------------------
    def test_code_verify_fail_when_saved_code_missing(self):
        cache.delete(f"verify:sms:password_reset:{self.phone}")

        res = self.client.post(
            self.code_verify_url,
            {"phone_number": self.phone, "purpose": "password_reset", "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.data)

    def test_code_verify_fail_when_code_mismatch(self):
        cache.set(f"verify:sms:password_reset:{self.phone}", "999999", timeout=300)

        res = self.client.post(
            self.code_verify_url,
            {"phone_number": self.phone, "purpose": "password_reset", "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res.data)

    def test_code_verify_success_sets_verify_ok_cache(self):
        cache.set(f"verify:sms:password_reset:{self.phone}", "123456", timeout=300)

        res = self.client.post(
            self.code_verify_url,
            {"phone_number": self.phone, "purpose": "password_reset", "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "인증이 성공하였습니다.")
        self.assertTrue(cache.get(f"verify:ok:password_reset:{self.phone}"))

    # -----------------------------
    # FindAccountView
    # -----------------------------
    def test_find_account_fail_when_not_verified(self):
        cache.delete(f"verify:ok:find_account:{self.phone}")
        cache.delete(f"verify:sms:find_account:{self.phone}")

        res = self.client.post(
            self.find_account_url, {"phone_number": self.phone}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "휴대폰 인증이 필요합니다.")

    def test_find_account_success(self):
        cache.set(f"verify:ok:find_account:{self.phone}", True, timeout=300)
        cache.set(f"verify:sms:find_account:{self.phone}", "123456", timeout=300)

        res = self.client.post(
            self.find_account_url, {"phone_number": self.phone}, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["exists"])
        self.assertIn("identifier", res.data)
        self.assertIn("@", res.data["identifier"])
        self.assertIn("*", res.data["identifier"])
        self.assertEqual(res.data["message"], "계정을 찾았습니다.")

        # 1회용 키 삭제 확인
        self.assertIsNone(cache.get(f"verify:ok:find_account:{self.phone}"))
        self.assertIsNone(cache.get(f"verify:sms:find_account:{self.phone}"))

    def test_find_account_user_not_found_returns_200_and_deletes_verify_keys(self):
        phone = "01099998888"
        cache.set(f"verify:ok:find_account:{phone}", True, timeout=300)
        cache.set(f"verify:sms:find_account:{phone}", "123456", timeout=300)

        res = self.client.post(
            self.find_account_url, {"phone_number": phone}, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["exists"])
        self.assertEqual(res.data["message"], "일치하는 계정을 찾을 수 없습니다.")

        self.assertIsNone(cache.get(f"verify:ok:find_account:{phone}"))
        self.assertIsNone(cache.get(f"verify:sms:find_account:{phone}"))

    # -----------------------------
    # PasswordResetRequestView
    # -----------------------------
    def test_password_reset_request_fail_when_not_verified(self):
        # ok 없음
        cache.delete(f"verify:ok:password_reset:{self.phone}")
        cache.set(f"verify:sms:password_reset:{self.phone}", "123456", timeout=300)

        res = self.client.post(
            self.reset_request_url,
            {"identifier": self.email, "phone_number": self.phone, "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "휴대폰 인증이 필요합니다.")

    def test_password_reset_request_fail_when_code_mismatch(self):
        cache.set(f"verify:ok:password_reset:{self.phone}", True, timeout=300)
        cache.set(f"verify:sms:password_reset:{self.phone}", "999999", timeout=300)

        res = self.client.post(
            self.reset_request_url,
            {"identifier": self.email, "phone_number": self.phone, "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data["detail"], "인증번호가 올바르지 않거나 만료되었습니다."
        )

    def test_password_reset_request_fail_when_user_not_found(self):
        cache.set(f"verify:ok:password_reset:{self.phone}", True, timeout=300)
        cache.set(f"verify:sms:password_reset:{self.phone}", "123456", timeout=300)

        res = self.client.post(
            self.reset_request_url,
            {
                "identifier": "wrong@example.com",
                "phone_number": self.phone,
                "code": "123456",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "일치하는 계정을 찾을 수 없습니다.")

    def test_password_reset_request_success_sets_cookie_and_caches_token_and_deletes_verify_keys(
        self,
    ):
        cache.set(f"verify:ok:password_reset:{self.phone}", True, timeout=300)
        cache.set(f"verify:sms:password_reset:{self.phone}", "123456", timeout=300)

        res = self.client.post(
            self.reset_request_url,
            {"identifier": self.email, "phone_number": self.phone, "code": "123456"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "비밀번호 재설정 요청이 확인되었습니다.")

        # 쿠키 발급 + 토큰 캐시 확인
        self.assertIn("pw_reset_token", res.cookies)
        token = res.cookies["pw_reset_token"].value
        self.assertTrue(token)
        self.assertEqual(cache.get(f"pw_reset:token:{token}"), self.user.id)

        # 인증 키 삭제 확인
        self.assertIsNone(cache.get(f"verify:ok:password_reset:{self.phone}"))
        self.assertIsNone(cache.get(f"verify:sms:password_reset:{self.phone}"))

    # -----------------------------
    # PasswordResetConfirmView
    # -----------------------------
    def test_password_reset_confirm_fail_when_cookie_missing(self):
        # serializer 통과 위해 confirm 포함
        res = self.client.post(
            self.reset_confirm_url,
            {"new_password": "NewPassword1!", "new_password_confirm": "NewPassword1!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "인증 정보가 없습니다.")

    def test_password_reset_confirm_fail_when_token_invalid_or_expired(self):
        self.client.cookies["pw_reset_token"] = "invalid-token"

        res = self.client.post(
            self.reset_confirm_url,
            {"new_password": "NewPassword1!", "new_password_confirm": "NewPassword1!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "유효하지 않거나 만료된 인증입니다.")

    def test_password_reset_confirm_fail_when_user_inactive(self):
        # 토큰 캐시는 있는데 user 조회(is_active=True)가 실패하도록 비활성화
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        token = "tokentest"
        cache.set(f"pw_reset:token:{token}", self.user.id, timeout=300)
        self.client.cookies["pw_reset_token"] = token

        res = self.client.post(
            self.reset_confirm_url,
            {"new_password": "NewPassword1!", "new_password_confirm": "NewPassword1!"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["detail"], "유효하지 않은 요청입니다.")

    def test_password_reset_confirm_success_changes_password_and_deletes_token(self):
        # 1) request 성공으로 토큰/쿠키 만들기
        cache.set(f"verify:ok:password_reset:{self.phone}", True, timeout=300)
        cache.set(f"verify:sms:password_reset:{self.phone}", "123456", timeout=300)

        req = self.client.post(
            self.reset_request_url,
            {"identifier": self.email, "phone_number": self.phone, "code": "123456"},
            format="json",
        )
        self.assertEqual(req.status_code, status.HTTP_200_OK)

        token = req.cookies["pw_reset_token"].value
        self.assertTrue(cache.get(f"pw_reset:token:{token}"))

        # 2) confirm 성공
        new_pw = "NewPassword1!"
        res = self.client.post(
            self.reset_confirm_url,
            {"new_password": new_pw, "new_password_confirm": new_pw},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "비밀번호가 성공적으로 변경되었습니다.")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pw))

        # 토큰 삭제
        self.assertIsNone(cache.get(f"pw_reset:token:{token}"))

        # delete_cookie 동작(존재만 확인)
        self.assertIn("pw_reset_token", res.cookies)
