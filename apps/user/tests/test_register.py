from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from apps.user.models import User
from apps.user.serializers.register import SignUpSerializer


class RegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/user/signup/"
        self.valid_data = {
            "password": "Password1!",
            "nickname": "테스터",
            "name": "tester",
            "gender": "M",
            "email_token": "etoken",
            "sms_token": "stoken",
        }

    def test_validate_password(self):
        serializer = SignUpSerializer()
        # 정상
        self.assertEqual(serializer.validate_password("Password1!"), "Password1!")
        # 길이가 짧을때
        with self.assertRaises(Exception):
            serializer.validate_password("Pwd!")
        # 대문자가 없을때
        with self.assertRaises(Exception):
            serializer.validate_password("password1!")
        # 연속으로 문자를 사용 했을 때
        with self.assertRaises(Exception):
            serializer.validate_password("abc123!!A")
        # 이메일 포함
        serializer.initial_data = {"email_token": "email@example.com"}
        with self.assertRaises(Exception):
            serializer.validate_password("password1!")

    def test_validate_nickname(self):
        serializer = SignUpSerializer()
        # 정상
        self.assertEqual(serializer.validate_nickname("tester"), "tester")
        # 길이가 짧을때
        with self.assertRaises(Exception):
            serializer.validate_nickname("A")
        # 길이가 길때
        with self.assertRaises(Exception):
            serializer.validate_nickname("A" * 20)
        # 허용 문자가 아닐때
        with self.assertRaises(Exception):
            serializer.validate_nickname("닉네임!!!")
        # 중복인 닉네임일때
        User.objects.create(
            email="a@b.com", nickname="중복닉네임", password="Password123!"
        )
        with self.assertRaises(Exception):
            serializer.validate_nickname("중복닉네임")

    @patch("apps.user.utils.tokens.TokenService.verify")
    def test_validate_tokens_and_duplication(self, mock_verify):
        serializer = SignUpSerializer(data={})

        def fake_verify(token, consume=True):  # 수정됨
            if token == "etoken":
                return "test@example.com"
            if token == "stoken":
                return "01012345678"
            return None

        mock_verify.side_effect = fake_verify
        attrs = {"email_token": "etoken", "sms_token": "stoken"}
        validated = serializer.validate(attrs)

        self.assertEqual(validated["email"], "test@example.com")
        self.assertEqual(validated["phone_number"], "01012345678")

        # 이메일 토큰 실패
        with self.assertRaises(Exception):
            serializer.validate({"email_token": "bad", "sms_token": "good"})

        # 중복 이메일
        User.objects.create(
            email="test@example.com", nickname="n", password="Password1!"
        )
        mock_verify.side_effect = lambda token, consume=True: (
            "test@example.com" if token == "etoken" else "01012345678"
        )
        with self.assertRaises(Exception):
            serializer.validate({"email_token": "etoken", "sms_token": "stoken"})

    def test_create_user(self):
        serializer = SignUpSerializer()
        validated_data = {
            "password": "Password1!",
            "nickname": "테스터",
            "name": "tester",
            "gender": "M",
            "email": "test@example.com",
            "phone_number": "01012345678",
            "sms_token": "stoken",
            "email_token": "etoken",
        }
        _ = serializer.create(validated_data)

        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertNotIn("email_token", validated_data)
        self.assertNotIn("sms_token", validated_data)

    @patch("apps.user.views.registerview.TokenService.create_token_pair")
    @patch("apps.user.utils.tokens.TokenService.verify")
    def test_register_view(self, mock_verify, mock_create_token):
        mock_create_token.return_value = ("refresh", "access")

        def fake_verify(token, consume=True):
            if token in ("etoken", "etoken2"):
                return "test@example.com"
            if token in ("stoken", "stoken2"):
                return "01012345678"
            return None

        mock_verify.side_effect = fake_verify

        data = self.valid_data.copy()

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)

        data["nickname"] = "A"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data["nickname"] = "닉네임2"
        data["email_token"] = "etoken2"
        data["sms_token"] = "stoken2"

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
