from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class MeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.me_url = "/api/v1/user/me"
        self.withdraw_url = "/api/v1/user/me/delete"

        self.password = "Password1234!"

        self.user = User.objects.create_user(
            email="test@example.com",
            password=self.password,
            nickname="닉네임",
            name="이름",
            gender="M",
            is_active=True,
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_get_me_success(self):
        self.authenticate()

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["nickname"], self.user.nickname)

    def test_put_me_success(self):
        self.authenticate()

        response = self.client.put(
            self.me_url,
            data={
                "nickname": "변경닉네임",
                "name": "변경이름",
                "gender": "M",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "변경닉네임")
        self.assertEqual(self.user.name, "변경이름")

    def test_patch_me_success(self):
        self.authenticate()

        response = self.client.patch(
            self.me_url,
            data={"nickname": "패치닉네임", "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "패치닉네임")

    def test_withdraw_success(self):
        self.authenticate()

        response = self.client.post(
            self.withdraw_url,
            data={"password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(self.user.email.startswith("deleted_"))
        self.assertFalse(self.user.has_usable_password())

    def test_withdraw_wrong_password(self):
        """비밀번호 틀리면 탈퇴 실패"""
        self.authenticate()

        response = self.client.post(
            self.withdraw_url,
            data={"password": "WrongPassword!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_withdraw_no_body(self):
        """password 없이 요청 시 실패"""
        self.authenticate()

        response = self.client.post(self.withdraw_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
