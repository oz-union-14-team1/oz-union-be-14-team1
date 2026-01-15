from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.community.services.review.review_like_service import (
    add_review_like,
    remove_review_like,
)
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

    def test_add_review_like(self):
        """
        좋아요 생성 로직 검증 (생성 및 멱등성)
        """
        # 1. 좋아요 생성
        count = add_review_like(self.user, self.review.id)

        self.assertEqual(count, 1)
        self.assertTrue(
            ReviewLike.objects.filter(user=self.user, review=self.review).exists()
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.like_count, 1)

        # 2. 중복 생성 요청 (이미 존재할 때) -> 개수 증가 없음
        count_2 = add_review_like(self.user, self.review.id)

        self.assertEqual(count_2, 1)  # 여전히 1이어야 함

    def test_remove_review_like(self):
        """
        좋아요 삭제 로직 검증
        """
        # 0. 좋아요 생성
        add_review_like(self.user, self.review.id)

        # 1. 좋아요 삭제
        count = remove_review_like(self.user, self.review.id)

        self.assertEqual(count, 0)
        self.assertFalse(
            ReviewLike.objects.filter(user=self.user, review=self.review).exists()
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.like_count, 0)

        # 2. 중복 삭제 요청 (이미 없을 때) -> 에러 없이 0 반환
        count_2 = remove_review_like(self.user, self.review.id)

        self.assertEqual(count_2, 0)

    def test_service_not_found(self):
        """
        존재하지 않는 리뷰 ID로 요청 시 예외 발생
        """
        invalid_id = 99999

        # POST 예외 확인
        with self.assertRaises(ReviewNotFound):
            add_review_like(self.user, invalid_id)

        # DELETE 예외 확인
        with self.assertRaises(ReviewNotFound):
            remove_review_like(self.user, invalid_id)
