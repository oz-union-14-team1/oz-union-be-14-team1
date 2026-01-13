from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.user.serializers.register import (
    RegisterSerializer,
    TEMP_EMAIL_CODES,
    TEMP_PHONE_CODES,
    FORBIDDEN_NICKNAMES,
)

User = get_user_model()


class RegisterSerializerTest(TestCase):

    def setUp(self):
        # 기본 유효 데이터
        self.email = "test@example.com"
        self.phone = "01012345678"

        TEMP_EMAIL_CODES[self.email] = {
            "code": "EMAIL123",
            "expires": datetime.now() + timedelta(minutes=10),
        }
        TEMP_PHONE_CODES[self.phone] = {
            "code": "PHONE123",
            "expires": datetime.now() + timedelta(minutes=10),
            "count": 1,
        }

        self.valid_data = {
            "email": self.email,
            "nickname": "ValidNick",
            "phone_number": self.phone,
            "gender": "M",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
            "email_code": "EMAIL123",
            "phone_code": "PHONE123",
        }

    def test_register_serializer_valid(self):
        """정상 데이터로 등록시 유저 생성"""
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.nickname, self.valid_data["nickname"])
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    def test_invalid_email(self):
        """잘못된 이메일 형식이면 오류 발생"""
        self.valid_data["email"] = "invalid-email"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_invalid_nickname(self):
        """잘못된 닉네임 형식이면 오류 발생"""
        self.valid_data["nickname"] = "!!badnick"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    def test_invalid_password(self):
        """약한 비밀번호 형식이면 오류 발생"""
        self.valid_data["password"] = "123223123"
        self.valid_data["password_confirm"] = "123223123"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_mismatched_password(self):
        """비밀번호 확인이 일치하지않으면 오류 발생"""
        self.valid_data["password_confirm"] = "StrongP@ss2"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_invalid_email_code(self):
        """이메일 인증 코드가 틀리면 오류 발생"""
        self.valid_data["email_code"] = "WRONGCODE"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email_code", serializer.errors)

    def test_invalid_phone_code(self):
        """휴대폰 인증이 틀리면 오류 발생"""
        self.valid_data["phone_code"] = "WRONGCODE"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_code", serializer.errors)

    def test_duplicate_email(self):
        """이미 존재하는 이메일"""
        User.objects.create_user(
            email=self.email, nickname="OtherNick", password="StrongP@ss1"
        )
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_forbidden_nickname(self):
        """금지된 닉네임이면 오류 발생"""
        for nick in FORBIDDEN_NICKNAMES:
            data = self.valid_data.copy()
            data["nickname"] = nick
            data["email"] = f"new_{nick}@example.com"
            serializer = RegisterSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("nickname", serializer.errors)

    def test_duplicate_nickname(self):
        """이미 존재하는 닉네임"""
        User.objects.create_user(
            email="other@example.com", nickname="ValidNick", password="StrongP@ss1"
        )
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    def test_invalid_phone_number_format(self):
        """잘못된 전화번호 형식"""
        self.valid_data["phone_number"] = "abcd1234"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_password_consecutive_chars(self):
        """연속된 문자/숫자 3개 이상 체크"""
        self.valid_data["password"] = "aaabbbCCC123!"
        self.valid_data["password_confirm"] = "aaabbbCCC123!"
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("password", serializer.errors)

    def test_password_contains_email(self):
        """비밀번호에 이메일 포함 체크"""
        self.valid_data["password"] = "test123Strong!"
        self.valid_data["password_confirm"] = "test123Strong!"
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("password", serializer.errors)

    def test_email_code_expired(self):
        """이메일 인증 코드 만료 체크"""
        TEMP_EMAIL_CODES[self.email]["expires"] = datetime.now() - timedelta(minutes=1)
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("email_code", serializer.errors)

    def test_phone_code_expired(self):
        """휴대폰 인증 코드 만료 체크"""
        TEMP_PHONE_CODES[self.phone]["expires"] = datetime.now() - timedelta(minutes=1)
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("phone_code", serializer.errors)

    def test_validate_email_format_exception(self):
        """validate_email_format에서 ValidationError 발생"""
        from unittest.mock import patch
        from django.core.exceptions import ValidationError as DjangoValidationError

        with patch(
            "apps.user.serializers.register.validate_email_format"
        ) as mock_validator:
            mock_validator.side_effect = DjangoValidationError("Invalid email")
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("email", serializer.errors)  # 60-61번 except 커버

    def test_validate_nickname_format_exception(self):
        """validate_nickname_format에서 ValidationError 발생"""
        from unittest.mock import patch
        from django.core.exceptions import ValidationError as DjangoValidationError

        with patch(
            "apps.user.serializers.register.validate_nickname_format"
        ) as mock_validator:
            mock_validator.side_effect = DjangoValidationError("Invalid nickname")
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("nickname", serializer.errors)  # 71-72번 except 커버

    def test_validate_phone_format_exception(self):
        """validate_phone_format에서 ValidationError 발생"""
        from unittest.mock import patch
        from django.core.exceptions import ValidationError as DjangoValidationError

        with patch(
            "apps.user.serializers.register.validate_phone_format"
        ) as mock_validator:
            mock_validator.side_effect = DjangoValidationError("Invalid phone")
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("phone_number", serializer.errors)  # 85-86번 except 커버
