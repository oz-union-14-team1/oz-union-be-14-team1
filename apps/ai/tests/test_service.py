from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from apps.user.models.user import User
from apps.game.models.game import Game
from apps.community.models.reviews import Review
from apps.ai.models import GameReviewSummary
from apps.ai.services import ReviewSummaryService
from apps.ai.exceptions.ai_exceptions import NotEnoughReviews, AiGenerationFailed


class ReviewSummaryServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.game = Game.objects.create(
            name="Test Game",
            intro="Intro",
            released_at=timezone.now(),
            developer="developer",
            avg_score=5.0,
        )

    def create_reviews(self, count):
        """테스트용 리뷰 일괄 생성 헬퍼"""
        for i in range(count):
            Review.objects.create(
                game=self.game, user=self.user, content=f"Review content {i}", rating=5
            )

    @patch("apps.ai.services.genai.Client")
    def test_get_summary_success_create_new(self, mock_client_class):
        """
        리뷰가 10개 이상일때, AI가 호출되어 새로운 요약이 생성되는지 테스트
        """
        # Given: 리뷰 10개 생성 및 AI 응답 Mocking 설정
        self.create_reviews(10)

        mock_response = MagicMock()
        mock_response.text = (
            '{"good_points": ["Good"], "bad_points": ["Bad"], "total_review": "Total"}'
        )

        mock_instance = mock_client_class.return_value
        mock_instance.models.generate_content.return_value = mock_response

        # When: 서비스의 요약 조회 메서드 호출
        service = ReviewSummaryService()
        result = service.get_summary(self.game.id)

        # Then: 결과 검증, DB 저장 확인, AI 호출 횟수 확인
        self.assertEqual(result["total_review"], "Total")
        self.assertTrue(GameReviewSummary.objects.filter(game=self.game).exists())
        mock_instance.models.generate_content.assert_called_once()

    @patch("apps.ai.services.genai.Client")
    def test_get_summary_return_cached_data(self, mock_client_class):
        """
        이미 최신 요약이 DB에 있다면, API 호출 없이 DB 데이터를 반환하는지 테스트
        """
        # Given: 리뷰 10개와 이미 생성된(캐싱된) 요약 데이터 존재
        self.create_reviews(10)
        GameReviewSummary.objects.create(
            game=self.game,
            text='{"good_points": ["Cached"], "bad_points": [], "total_review": "Cached Review"}',
        )
        mock_instance = mock_client_class.return_value

        # When: 서비스 메서드 호출
        service = ReviewSummaryService()
        result = service.get_summary(self.game.id)

        # Then: 캐싱된 데이터 반환 확인 및 API 호출이 0회인지 검증
        self.assertEqual(result["good_points"][0], "Cached")
        mock_instance.models.generate_content.assert_not_called()

    @patch("apps.ai.services.genai.Client")
    def test_not_enough_reviews_exception(self, mock_client_class):
        """
        리뷰가 10개 미만일 때 NotEnoughReviews 예외가 발생하는지 테스트
        """
        # Given: 리뷰가 5개밖에 없는 상황
        self.create_reviews(5)
        service = ReviewSummaryService()

        # When & Then: 메서드 호출 시 NotEnoughReviews 예외 발생 검증
        with self.assertRaises(NotEnoughReviews):
            service.get_summary(self.game.id)

    @patch("apps.ai.services.genai.Client")
    def test_ai_generation_failed(self, mock_client_class):
        """
        AI API 호출 중 에러 발생 시 AiGenerationFailed 예외 처리 테스트
        """
        # Given: 리뷰는 충분하지만, AI Client가 에러를 뱉도록 설정
        self.create_reviews(10)
        mock_instance = mock_client_class.return_value
        mock_instance.models.generate_content.side_effect = Exception(
            "Google API Error"
        )
        service = ReviewSummaryService()

        # When & Then: 메서드 호출 시 AiGenerationFailed 예외 발생 검증
        with self.assertRaises(AiGenerationFailed):
            service.get_summary(self.game.id)
