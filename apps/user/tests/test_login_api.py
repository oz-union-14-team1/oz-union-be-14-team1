# apps/user/tests/test_login.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from apps.user.serializers.login import LoginSerializer, LOGIN_FAILED_MESSAGE

User = get_user_model()


class LoginSerializerTest(TestCase):
    """
    LoginSerializer.validate 단위 테스트
    """

    def setUp(self):
        self.password = "Password1234!!"
        self.user = User.objects.create_user(
            email="test@example.com",
            password=self.password,
            is_active=True,
        )

    def test_login_success(self):
        """로그인 성공"""
        serializer = LoginSerializer(
            data={
                "email": "test@example.com",
                "password": self.password,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_login_fail_email_not_exists(self):
        """존재하지 않는 이메일"""
        serializer = LoginSerializer(
            data={
                "email": "wrong@example.com",
                "password": self.password,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["detail"][0],
            LOGIN_FAILED_MESSAGE,
        )

    def test_login_fail_wrong_password(self):
        """비밀번호 오류"""
        serializer = LoginSerializer(
            data={
                "email": "test@example.com",
                "password": "WrongPassword123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["detail"][0],
            LOGIN_FAILED_MESSAGE,
        )

    def test_login_fail_inactive_user(self):
        """비활성(탈퇴) 계정"""
        self.user.is_active = False
        self.user.save()

        serializer = LoginSerializer(
            data={
                "email": "test@example.com",
                "password": self.password,
            }
        )

        with self.assertRaises(PermissionDenied):
            serializer.is_valid(raise_exception=True)


class LoginViewTest(TestCase):
    """
    LoginView.post 통합 흐름 테스트
    """

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/user/login/"  # 실제 URL에 맞게 수정

        self.password = "Password1234!!"
        self.user = User.objects.create_user(
            email="test@example.com",
            password=self.password,
            is_active=True,
        )

    @patch("apps.user.views.LoginView.TokenService.create_token_pair")
    def test_login_success(self, mock_create_access_token):
        """로그인 성공 → access_token 반환"""
        mock_create_access_token.return_value = (
            "fake-refresh-token",
            "fake-access-token",
        )

        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["access_token"], "fake-access-token")
        self.assertIn("refresh_token", response.cookies)
        mock_create_access_token.assert_called_once()

    def test_login_fail_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("detail", response.data["errors"])

    def test_login_fail_email_not_exists(self):
        response = self.client.post(
            self.url,
            {
                "email": "wrong@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("detail", response.data["errors"])

    def test_login_fail_inactive_user(self):
        """비활성 계정"""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
