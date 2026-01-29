from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status, serializers

from django.contrib.auth import get_user_model
from apps.user.serializers.register import SignUpSerializer

User = get_user_model()


class RegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/user/signup"
        self.valid_data = {
            "email": "test@example.com",
            "password": "Password1!",
            "nickname": "테스터",
            "name": "tester",
            "gender": "M",
            "phone_number": "01012345678",
        }

    def test_validate_password(self):
        serializer = SignUpSerializer()
        # 정상 케이스
        self.assertEqual(serializer.validate_password("Password1!"), "Password1!")
        # 8자 미만
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_password("Pwd1!")
        # 대문자 없음
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_password("password1!")
        # 특수문자 없음
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_password("Password12")

    def test_validate_nickname(self):
        serializer = SignUpSerializer()
        # 정상
        self.assertEqual(serializer.validate_nickname("tester"), "tester")
        # 길이 제한 실패
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_nickname("A")
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_nickname("A" * 20)
        # 허용 문자가 아닐 때
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_nickname("닉네임!!!")
        # 중복 닉네임
        User.objects.create_user(
            email="a@b.com",
            password="Password123!",
            nickname="중복닉",
            name="x",
            gender="M",
            phone_number="01099998888",
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_nickname("중복닉")

    def test_validate_email_duplication(self):
        # 중복 이메일
        User.objects.create_user(  # ✅ 수정됨
            email="test@example.com",
            password="Password1!",
            nickname="n1",
            name="x",
            gender="M",
            phone_number="01011112222",
        )
        serializer = SignUpSerializer(data=self.valid_data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_phone_number_normalizes_and_checks_duplication(self):
        serializer = SignUpSerializer()
        self.assertEqual(
            serializer.validate_phone_number("010-1234-5678"), "01012345678"
        )

        User.objects.create_user(
            email="dup_phone@b.com",
            password="Password1!",
            nickname="폰중복",
            name="x",
            gender="M",
            phone_number="01012345678",
        )
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_phone_number("010-1234-5678")

    def test_create_user(self):
        serializer = SignUpSerializer()
        validated_data = self.valid_data.copy()
        user = serializer.create(validated_data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        self.assertEqual(user.nickname, "테스터")
        self.assertEqual(user.name, "tester")
        self.assertEqual(user.phone_number, "01012345678")

    def test_register_view_success(self):
        # 정상 회원가입
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "회원가입이 완료되었습니다.")

        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.phone_number, "01012345678")

    def test_register_view_invalid_nickname(self):
        # 잘못된 닉네임 400
        data = self.valid_data.copy()
        data["nickname"] = "A"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)

    def test_register_view_duplicate_email(self):
        # 중복 이메일 400
        User.objects.create_user(
            email="test@example.com",
            password="Password1!",
            nickname="n1",
            name="x",
            gender="M",
            phone_number="01011112222",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_detail", response.data)
