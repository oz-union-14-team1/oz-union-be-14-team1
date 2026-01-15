from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.community.models.reviews import Review
from apps.game.models.game import Game

User = get_user_model()


class ReviewLikeServiceTest(APITestCase):
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

        self.url = reverse("review_like", kwargs={"review_id": self.review.id})

    def test_post_review_like_success(self):
        """
        좋아요 등록 성공 (201 Created)
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_liked"])
        self.assertEqual(response.data["like_count"], 1)
        self.assertEqual(response.data["message"], "좋아요를 눌렀습니다.")

        # 한 번 더 요청해도 개수가 늘어나지 않은지 확인
        response_2 = self.client.post(self.url)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.data["like_count"], 1)

    def test_delete_review_like_success(self):
        """
        좋아요 취소 성공 (200 OK)
        """
        self.client.force_authenticate(user=self.user)

        # 1. 좋아요 생성
        self.client.post(self.url)

        # 2. 좋아요 취소 요청 (DELETE 메서드 사용)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_liked"])
        self.assertEqual(response.data["like_count"], 0)
        self.assertEqual(response.data["message"], "좋아요를 취소했습니다.")

    def test_api_unauthorized(self):
        """
        비로그인 유저 요청 시 차단 (401 Unauthorized)
        """
        # POST 요청
        response_post = self.client.post(self.url)
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

        # DELETE 요청
        response_delete = self.client.delete(self.url)
        self.assertEqual(response_delete.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_not_found(self):
        """
        존재하지 않는 리뷰에 요청 시 404 Not Found
        """
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse("review_like", kwargs={"review_id": 99999})

        # POST
        response_post = self.client.post(wrong_url)
        self.assertEqual(response_post.status_code, status.HTTP_404_NOT_FOUND)

        # DELETE
        response_delete = self.client.delete(wrong_url)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)
