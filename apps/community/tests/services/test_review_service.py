from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.community.exceptions.review_exceptions import GameNotFound
from apps.community.services.review.review_create_service import create_review
from apps.community.models.reviews import Review
from apps.game.models.game import Game

User = get_user_model()


class ReviewServiceTest(TestCase):
    def setUp(self):
        """
        테스트 시작 전 공통 데이터 생성
        """
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )

        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())

    def test_create_review_success(self):
        """
        정상적인 데이터로 리뷰 생성 성공
        """
        # Given: 리뷰 생성에 필요한 데이터 준비
        data = {"content": "그저 그런데요?", "rating": 2}

        # When: 서비스 로직 실행
        review = create_review(
            author=self.user, game_id=self.game.id, validated_data=data
        )

        # Then: 리뷰가 정상적으로 생성되었는지 검증
        self.assertIsNotNone(review.id)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.game, self.game)
        self.assertEqual(review.content, "그저 그런데요?")
        self.assertEqual(review.rating, 2)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_game_not_found(self):
        """
        존재하지 않는 게임 ID로 요청 시 404
        """
        # Given: 존재하지 않는 게임 ID와 데이터 준비
        invalid_game_id = 9999
        data = {"content": "재밌음", "rating": 5}

        # When & Then: 예외가 발생하는지 확인
        with self.assertRaises(GameNotFound):
            create_review(
                author=self.user, game_id=invalid_game_id, validated_data=data
            )
