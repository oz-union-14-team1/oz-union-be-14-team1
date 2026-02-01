from django.test import TestCase
from apps.ai.utils import is_valid_review_for_ai


class ProfanityFilterTest(TestCase):
    """
    is_valid_review_for_ai 함수 테스트
    1. 욕설 O + 짧음(<10자) -> False (필터링)
    2. 욕설 O + 김(>=10자) -> True (통과)
    3. 욕설 X -> True (통과)
    """

    def test_short_bad_words_filtered(self):
        """1. 짧은 욕설(10자 미만)은 False 반환"""
        bad_shorts = [
            "시발",
            "시.발",
            "개새끼",
            "미친놈",
            "병신",
            "ㅗㅗㅗㅗ",
        ]
        for word in bad_shorts:
            with self.subTest(word=word):
                self.assertFalse(
                    is_valid_review_for_ai(word), f"필터링 실패(통과됨): {word}"
                )

    def test_long_bad_words_passed(self):
        """2. 긴 욕설(10자 이상)은 True 반환 (정보 가치 인정)"""
        bad_longs = [
            "시발 게임이 너무 재미없어서 화가 난다",  # 19자
            "운영자가 개새끼지만 게임성은 좋다",  # 17자
            "이런 병신 같은 버그가 아직도 있네",  # 18자
            "솔직히 존나 재미없음 환불좀",  # 15자
        ]
        for word in bad_longs:
            with self.subTest(word=word):
                self.assertTrue(
                    is_valid_review_for_ai(word), f"통과 실패(필터링됨): {word}"
                )

    def test_normal_words_passed(self):
        """3. 일반적인 단어는 길이에 상관없이 True 반환"""
        normals = [
            "안녕하세요",  # 짧은 정상
            "갓겜",  # 매우 짧은 정상
            "정말 재미있는 게임입니다 추천해요",  # 긴 정상
            "타격감이 훌륭하고 그래픽이 좋아요",
        ]
        for word in normals:
            with self.subTest(word=word):
                self.assertTrue(
                    is_valid_review_for_ai(word), f"오탐지(필터링됨): {word}"
                )
