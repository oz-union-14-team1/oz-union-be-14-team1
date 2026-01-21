from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_framework.permissions import AllowAny
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


@override_settings(
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_db",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
)
class LoginAPIViewTest(APITestCase):
    permission_classes = [AllowAny]

    def setUp(self):
        self.password = "Password1234@@"

        self.user = User.objects.create_user(
            email="test@example.com",
            password=self.password,
            nickname="tester",
            name="테스터",
            phone_number="01012345678",
            gender="M",
            is_active=True,
        )

        self.login_url = reverse("user:login")

    # 로그인 성공 테스트
    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    # 비밀번호 누락
    def test_login_without_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["error_detail"])

    # 이메일 누락
    def test_login_without_email(self):
        response = self.client.post(
            self.login_url,
            {
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error_detail"])

    # 비밀번호 틀림
    def test_login_wrong_password(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error_detail"]["detail"],
            "이메일 또는 비밀번호가 잘못 되었습니다.",
        )

    # 탈퇴(비활성화된) 계정
    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error_detail"]["detail"],
            "탈퇴 신청한 계정입니다.",
        )

    # 존재하지 않는 이메일
    def test_login_email_not_exists(self):
        response = self.client.post(
            self.login_url,
            {
                "email": "not_exist@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error_detail"]["detail"],
            "이메일 또는 비밀번호가 잘못되었습니다.",
        )
