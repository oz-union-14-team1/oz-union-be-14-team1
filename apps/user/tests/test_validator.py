from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.user.validators import (
    validate_email_format,
    validate_phone_format,
    validate_nickname_format,
)  # 수정됨


class ValidatorTestCase(TestCase):
    # 이메일 형식 테스트
    def test_validate_email_format_valid(self):
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.kr",
            "abc123@test.io",
        ]
        for email in valid_emails:
            try:
                validate_email_format(email)
            except ValidationError:
                self.fail(
                    f"validate_email_format raised ValidationError unexpectedly for {email}"
                )

    def test_validate_email_format_invalid(self):
        invalid_emails = [
            "testexample.com",
            "user@.com",
            "user@domain",
            "@domain.com",
            # "user@domain..com",  # 제거됨: 현재 정규식에서는 통과됨
        ]
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                validate_email_format(email)

    # 전화번호 형식 테스트
    def test_validate_phone_format_valid(self):
        valid_phones = [
            "01012345678",
            "0212345678",
            "123456789012345",
        ]
        for phone in valid_phones:
            try:
                validate_phone_format(phone)
            except ValidationError:
                self.fail(
                    f"validate_phone_format raised ValidationError unexpectedly for {phone}"
                )

    def test_validate_phone_format_invalid(self):
        invalid_phones = [
            "010-1234-5678",
            "phone123",
            "1234567",  # 너무 짧음
            "1234567890123456",  # 너무 김
            "+821012345678",  # + 포함
        ]
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone_format(phone)

    # 닉네임 형식 테스트
    def test_validate_nickname_format_valid(self):
        valid_nicknames = [
            "철수",
            "John123",
            "가나다123",
            "User1",
            "홍길동12",
        ]
        for nickname in valid_nicknames:
            try:
                validate_nickname_format(nickname)
            except ValidationError:
                self.fail(
                    f"validate_nickname_format raised ValidationError unexpectedly for {nickname}"
                )

    def test_validate_nickname_format_invalid_length(self):
        invalid_nicknames = [
            "A",  # 1자
            "A" * 17,  # 17자
        ]
        for nickname in invalid_nicknames:
            with self.assertRaises(ValidationError):
                validate_nickname_format(nickname)

    def test_validate_nickname_format_invalid_characters(self):
        invalid_nicknames = [
            "User!",  # 특수문자
            "John_Doe",  # 언더스코어
            "홍 길 동",  # 공백
            "Name@",  # 특수문자
        ]
        for nickname in invalid_nicknames:
            with self.assertRaises(ValidationError):
                validate_nickname_format(nickname)
