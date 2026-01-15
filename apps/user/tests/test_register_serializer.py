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
        self.email = "test@example.com"
        self.phone_number = "01033211545"

        TEMP_EMAIL_CODES[self.email] = {
            "code": "EMAIL123",
            "expires": datetime.now() + timedelta(minutes=10),
        }
        TEMP_PHONE_CODES[self.phone_number] = {
            "code": "PHONE123",
            "expires": datetime.now() + timedelta(minutes=10),
            "count": 1,
        }

        self.valid_data = {
            "email": self.email,
            "nickname": "ValidNick",
            "name": "양민석",
            "birthday": "2000-11-21",
            "gender": "M",
            "phone_number": self.phone_number,
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
            "email_token": "EMAIL123",
            "sms_token": "PHONE123",
        }

    # 정상 작동 하는지 테스트
    def test_register_serializer_valid(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.nickname, self.valid_data["nickname"])
        self.assertEqual(user.phone_number, self.valid_data["phone_number"])
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    # 이메일 형식 테스트 (이상한 이메일이면 오류 발생)
    def test_invalid_email_format(self):
        self.valid_data["email"] = "invalid-email"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    # 닉네임 형식 테스트 ( 닉네임 형식 잘못되면 오류 발생)
    def test_invalid_nickname_format(self):
        self.valid_data["nickname"] = "!!badnick"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    # 약한 비밀번호면 오류 발생 테스트
    def test_invalid_password(self):
        self.valid_data["password"] = "123223123"
        self.valid_data["password_confirm"] = "123223123"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    # 비밀번호확인이 맞지않으면 오류 발생 테스트
    def test_mismatched_password(self):
        self.valid_data["password_confirm"] = "StrongP@ss2"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    # 이메일 토큰이 틀리면 오류 발생 테스트
    def test_invalid_email_token(self):
        self.valid_data["email_token"] = "WRONGCODE"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email_token", serializer.errors)

    # SMS 인증 토큰이 틀리면 오류 발생 테스트
    def test_invalid_sms_token(self):
        self.valid_data["sms_token"] = "WRONGCODE"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("sms_token", serializer.errors)

    # 이미 존재하는 이메일이면 오류 발생 테스트
    def test_duplicate_email(self):
        User.objects.create_user(
            email=self.email, nickname="OtherNick", password="StrongP@ss1"
        )
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    # 금지된 닉네임이면 오류 발생
    def test_forbidden_nickname(self):
        for nick in FORBIDDEN_NICKNAMES:
            data = self.valid_data.copy()
            data["nickname"] = nick
            data["email"] = f"new_{nick}@example.com"
            serializer = RegisterSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("nickname", serializer.errors)

    # 이미 닉네임이 존재하는지 테스트
    def test_duplicate_nickname(self):
        User.objects.create_user(
            email="other@example.com", nickname="ValidNick", password="StrongP@ss1"
        )
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("nickname", serializer.errors)

    # 비밀번호에 연속된 문자/숫자가 3개이상이면 오류발생 테스트
    def test_password_consecutive_chars(self):
        self.valid_data["password"] = "aaabbbCCC123!"
        self.valid_data["password_confirm"] = "aaabbbCCC123!"
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("password", serializer.errors)

    # 비밀번호에 이메일주소의 일부가 들어가면 오류발생 하는 테스트
    def test_password_contains_email(self):
        self.valid_data["password"] = "test123Strong!"
        self.valid_data["password_confirm"] = "test123Strong!"
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("password", serializer.errors)

    ############################# 토큰 만료 테스트
    # 이메일 인증 코드 만료 테스트
    def test_email_token_expired(self):
        TEMP_EMAIL_CODES[self.email]["expires"] = datetime.now() - timedelta(minutes=1)
        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()
        self.assertIn("email_token", serializer.errors)

    # SMS 인증 코드 만료 테스트
    def test_sms_token_expired(self):
        TEMP_PHONE_CODES[self.phone_number]["expires"] = datetime.now() - timedelta(
            minutes=1
        )

        serializer = RegisterSerializer(data=self.valid_data)
        serializer.is_valid()

        self.assertIn("sms_token", serializer.errors)

    ######################입력값 예외 발생시 오류 처리 테스트
    # 이메일 포맷에서 validationerror가 발생했을 때 처리 테스트
    def test_validate_email_format_exception(self):
        from unittest.mock import patch
        from django.core.exceptions import ValidationError as DjangoValidationError

        with patch(
            "apps.user.serializers.register.validate_email_format"
        ) as mock_validator:
            mock_validator.side_effect = DjangoValidationError("Invalid email")
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("email", serializer.errors)

    # 닉네임 포맷에서 validationerror가 발생했을 때 처리 테스트
    def test_validate_nickname_format_exception(self):
        from unittest.mock import patch
        from django.core.exceptions import ValidationError as DjangoValidationError

        with patch(
            "apps.user.serializers.register.validate_nickname_format"
        ) as mock_validator:
            mock_validator.side_effect = DjangoValidationError("Invalid nickname")
            serializer = RegisterSerializer(data=self.valid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn("nickname", serializer.errors)

    # SMS 토큰 포맷 검증 실패 오류 발생
    def test_validate_sms_token_format_exception(self):
        self.valid_data["sms_token"] = "INVALID"
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("sms_token", serializer.errors)
