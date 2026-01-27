from django.test import TestCase
from apps.ai.services.review_summary_service import ReviewSummaryService
from unittest.mock import patch


class ProfanityFilterTest(TestCase):
    def setUp(self):
        with patch("apps.ai.services.genai.Client"):
            self.service = ReviewSummaryService()
            self.pattern = self.service.profanity_pattern

    def test_bad_words_detection(self):
        """욕설이 제대로 잡히는지 테스트"""
        bad_examples = [
            "시발",
            "시.발",
            "시1발",
            "와 시@발",
            "개새끼",
            "개.새.끼",
            "개1새2끼",
            "병신",
            "병.신",
            "야이 븅신아",
            "미친",
            "미.친",
            "지랄",
            "염병",
            "느금마",
            "니미",
            "좆",
            "좃",
        ]
        for word in bad_examples:
            with self.subTest(word=word):
                self.assertTrue(self.pattern.search(word), f"못 잡은 욕설: {word}")

    def test_normal_words_safety(self):
        """정상적인 단어가 오해받지 않는지 테스트 (True Negative)"""
        good_examples = [
            "시린발",
            "시골발",
            "병원신",
            "등신대",
            "미나리친구",
            "염소병",
            "병",
        ]
        for word in good_examples:
            with self.subTest(word=word):
                self.assertFalse(self.pattern.search(word), f"잡힌 단어: {word}")
