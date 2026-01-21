from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserManagerTestCase(TestCase):
    def test_create_user_with_password(self):
        # 일반사용자 생성시 이메일 + 비밀번호가 올바르게 설정되었는지 검증
        email = "test@example.com"
        password = "securepassword"

        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_without_password(self):
        # 비밀번호 없이 생성 시 비밀번호가 없음을 처리 하는 테스트
        email = "nopass@example.com"

        user = User.objects.create_user(email=email, password=None)

        self.assertEqual(user.email, email)
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_no_email(self):
        # 이건 이메일 버전
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="1234")

    def test_create_superuser_defaults(self):
        #슈퍼유저 생성시 이메일 + 비밀번호가 올바르게 설정되었는지 검증
        email = "admin@example.com"
        password = "adminpass"

        admin = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(admin.email, email)
        self.assertTrue(admin.check_password(password))
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
