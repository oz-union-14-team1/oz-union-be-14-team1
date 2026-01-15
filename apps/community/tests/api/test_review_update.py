from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.community.models.reviews import Review
from apps.game.models.game import Game
from django.utils import timezone

User = get_user_model()


class ReviewUpdateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.other_user = User.objects.create_user(
            email="test1@test.com",
            password="test1234",
            nickname="test_user1",
            phone_number="010-0000-0001",
        )
        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.review = Review.objects.create(
            user=self.user, game=self.game, content="재밌어요", rating=5
        )

        self.url = reverse("review_update", kwargs={"review_id": self.review.id})

    def test_update_review_success(self):
        """
        작성자 본인의 리뷰 수정 성공
        """
        self.client.force_authenticate(user=self.user)
        data = {"content": "New Content"}

        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.content, "New Content")
        self.assertEqual(self.review.rating, 5)

    def test_update_review_permission_denied(self):
        """
        다른 유저가 수정 시도 시 403 Forbidden
        """
        self.client.force_authenticate(user=self.other_user)
        data = {"content": "Hacked"}

        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
