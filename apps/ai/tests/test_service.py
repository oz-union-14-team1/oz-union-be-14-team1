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

    @patch("apps.ai.services.genai.Client")
    def test_filter_profanity_before_ai_call(self, mock_client_class):
        """
        욕설이 포함된 리뷰는 AI 요약 요청 데이터에서 제외되는지 테스트
        """
        # Given: 정상 리뷰 3개 + 욕설 리뷰 2개 생성 (총 5개)
        Review.objects.create(
            game=self.game,
            user=self.user,
            content="정말 재미있는 게임입니다.",
            rating=5,
        )
        Review.objects.create(
            game=self.game, user=self.user, content="이건 진짜로 시1발 망겜임", rating=1
        )  # 욕설
        Review.objects.create(
            game=self.game, user=self.user, content="그래픽이 엄청 훌륭해요.", rating=5
        )
        Review.objects.create(
            game=self.game, user=self.user, content="운영자가 진짜 개.새.끼임", rating=1
        )  # 욕설
        Review.objects.create(
            game=self.game,
            user=self.user,
            content="타격감과 스토리가 좋아요.",
            rating=5,
        )

        # AI 응답 Mock 설정 (성공 케이스)
        mock_instance = mock_client_class.return_value
        mock_instance.models.generate_content.return_value.text = "{}"

        # When: 서비스 호출
        service = ReviewSummaryService()

        service.min_review_count = 1
        service.get_summary(self.game.id)

        # Then: AI에게 전달된 프롬프트 내용 확인
        call_args = mock_instance.models.generate_content.call_args
        prompt_text = call_args.kwargs["contents"]

        # 1. 욕설 리뷰 내용은 없어야 함
        self.assertNotIn("시1발", prompt_text)
        self.assertNotIn("개.새.끼", prompt_text)

        # 2. 정상 리뷰 내용은 있어야 함
        self.assertIn("정말 재미있는 게임입니다.", prompt_text)
        self.assertIn("그래픽이 엄청 훌륭해요.", prompt_text)
