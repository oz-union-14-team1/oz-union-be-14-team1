from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.community.services.review_like_service import create_review_like
from apps.community.models.reviews import Review
from apps.community.models.review_like import ReviewLike
from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.game.models.game import Game

User = get_user_model()


class ReviewLikeServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.review = Review.objects.create(
            user=self.user, game=self.game, content="재밌어요", rating=5
        )

    def test_review_like_success(self):
        """
        좋아요 기능 검증 (생성 -> 삭제)
        """
        # 1. 좋아요 생성 (Like)
        is_liked, count = create_review_like(self.user, self.review.id)

        self.assertTrue(is_liked)
        self.assertEqual(count, 1)
        self.assertTrue(
            ReviewLike.objects.filter(user=self.user, review=self.review).exists()
        )

        # 리뷰 객체 갱신 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.like_count, 1)

        # 2. 좋아요 취소 (Unlike)
        is_liked_2, count_2 = create_review_like(self.user, self.review.id)

        self.assertFalse(is_liked_2)
        self.assertEqual(count_2, 0)
        self.assertFalse(
            ReviewLike.objects.filter(user=self.user, review=self.review).exists()
        )

        # 리뷰 객체 갱신 확인
        self.review.refresh_from_db()
        self.assertEqual(self.review.like_count, 0)

    def test_review_like_not_found(self):
        """
        존재하지 않는 리뷰 ID로 요청 시 ReviewNotFound 예외 발생
        """
        invalid_id = 99999

        with self.assertRaises(ReviewNotFound):
            create_review_like(self.user, invalid_id)
