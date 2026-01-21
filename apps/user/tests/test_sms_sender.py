from django.test import TestCase
from unittest.mock import patch
from apps.user.utils.sender import SMSSender


class SMSSenderTestCase(TestCase):
    # 모킹 : 실제 동작을 하지않고 함수나 객체를 흉내 내어서 호출 여부와 입력값만 검증하는것.
    @patch("apps.user.utils.sender.telnyx")  # telnyx 모듈 전체를 런타임 모킹
    def test_send_verification_code_calls_telnyx(self, mock_telnyx):
        phone = "01012345678"
        code = "123456"

        # Message.create 모킹
        mock_telnyx.Message.create.return_value = None

        # 테스트 대상 함수 호출
        SMSSender.send_verification_code(phone, code)

        # Message.create가 호출됐는지 검증
        mock_telnyx.Message.create.assert_called_once()
        args, kwargs = mock_telnyx.Message.create.call_args
        self.assertEqual(kwargs["to"], phone)
        self.assertIn(code, kwargs["text"])
