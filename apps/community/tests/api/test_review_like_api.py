# apps/community/tests/api/test_review_like_api.py

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.community.models.reviews import Review
from apps.game.models.game import Game

User = get_user_model()


class ReviewLikeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.game = Game.objects.create(name="Game1", released_at=timezone.now())
        self.review = Review.objects.create(
            user=self.user, game=self.game, content="Good", rating=5
        )
        self.url = reverse("review_like", kwargs={"review_id": self.review.id})

    def test_post_review_like_success(self):
        """
        로그인 유저의 좋아요 요청 성공 (200 OK)
        """
        self.client.force_authenticate(user=self.user)

        # 1. 좋아요 요청
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_liked"])
        self.assertEqual(response.data["like_count"], 1)
        self.assertEqual(response.data["message"], "성공적으로 반영되었습니다.")

        # 2. 좋아요 취소 요청 (한 번 더 POST)
        response_2 = self.client.post(self.url)

        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertFalse(response_2.data["is_liked"])  # False 확인
        self.assertEqual(response_2.data["like_count"], 0)  # 0 확인

    def test_post_like_unauthorized(self):
        """
        비로그인 유저 요청 시 차단 (401 Unauthorized)
        """

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_like_not_found(self):
        """
        존재하지 않는 리뷰에 요청 시 404 Not Found
        """
        self.client.force_authenticate(user=self.user)

        wrong_url = reverse("review_like", kwargs={"review_id": 99999})
        response = self.client.post(wrong_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 리뷰입니다.")
