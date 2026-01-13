from django.test import TestCase
from django.http import Http404
from apps.community.services.review_create_service import create_review
from apps.community.models.reviews import Review
from apps.game.models.game import Game
from apps.user.models.user import User

class ReviewServiceTest(TestCase):
    def setUp(self):
        """
        테스트 시작 전 공통 데이터 생성
        """
        self.user = User.objects.create_user(
            nickname="극성 테스터",
            password="password",
            email="tester@test.com" # (선택) 이메일도 필요하면 추가
        )
        self.game = Game.objects.create(name="Test Game")

    def test_create_review_success(self):
        """
        정상적인 데이터로 리뷰 생성 성공
        """
        data = {
            "content": "그저 그런데요?",
            "rating": 2
        }

        review = create_review(
            author=self.user,
            game_id=self.game.id,
            validated_data=data
        )

        self.assertIsNotNone(review.id)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.game, self.game)
        self.assertEqual(review.content, "그저 그런데요?")
        self.assertEqual(review.rating, 2)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_game_not_found(self):
        """
        존재하지 않는 게임 ID로 요청 시 404 발생
        """
        invalid_game_id = 9999
        data = {"content": "재밌음", "rating": 5}

        with self.assertRaises(Http404):
            create_review(
                author=self.user,
                game_id=invalid_game_id,
                validated_data=data
            )