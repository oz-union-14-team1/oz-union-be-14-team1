from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class MeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/user/me/"

        self.user = User.objects.create_user(
            email="test@example.com",
            password="Password1234!",
            nickname="닉네임",
            name="이름",
            gender="M",
            is_active=True,
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_get_me_success(self):
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["nickname"], self.user.nickname)
        self.assertEqual(response.data["name"], self.user.name)
        self.assertEqual(response.data["gender"], self.user.gender)

    def test_get_me_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_me_success(self):
        self.authenticate()
        response = self.client.patch(
            self.url,
            data={"nickname": "변경된닉네임", "password": "Password1234!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "변경된닉네임")

    def test_patch_email_not_allowed(self):
        self.authenticate()
        response = self.client.patch(
            self.url,
            data={"email": "changed@example.com", "password": "Password1234!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")

    def test_patch_me_wrong_password(self):
        self.authenticate()
        response = self.client.patch(
            self.url,
            data={"nickname": "닉네임변경", "password": "WrongPassword!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["errors"])
        self.assertEqual(
            response.data["errors"]["password"][0], "비밀번호가 올바르지 않습니다."
        )

    def test_password_change_not_allowed(self):
        self.authenticate()
        response = self.client.patch(
            self.url,
            data={"password": "NewPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["errors"])
        self.assertEqual(
            response.data["errors"]["password"][0], "비밀번호가 올바르지 않습니다."
        )

    def test_put_me_success(self):
        self.authenticate()
        response = self.client.put(
            self.url,
            data={
                "nickname": "새닉네임",
                "name": "새이름",
                "gender": "F",
                "password": "Password1234!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "새닉네임")
        self.assertEqual(self.user.name, "새이름")
        self.assertEqual(self.user.gender, "F")

    def test_put_me_wrong_password(self):
        self.authenticate()
        response = self.client.put(
            self.url,
            data={
                "nickname": "닉네임변경",
                "name": "이름변경",
                "gender": "F",
                "password": "WrongPassword!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data["errors"])
        self.assertEqual(
            response.data["errors"]["password"][0], "비밀번호가 올바르지 않습니다."
        )

    def test_delete_me_success(self):
        self.authenticate()
        response = self.client.delete(
            self.url,
            data={"password": "Password1234!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_delete_me_wrong_password(self):
        self.authenticate()
        response = self.client.delete(
            self.url,
            data={"password": "WrongPassword!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_delete_me_no_body(self):
        """DELETE 요청에 body 없이 호출 시 400 에러 발생"""
        self.authenticate()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
