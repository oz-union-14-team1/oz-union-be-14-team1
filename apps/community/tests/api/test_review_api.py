from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.game.models.game import Game
from apps.user.models.user import User
from apps.community.models.reviews import Review


class GameReviewAPITest(APITestCase):
    def setUp(self):
        """
        테스트 데이터 초기화
        """
        self.game = Game.objects.create(name="Elden Ring")
        self.url = reverse("game_review_create", kwargs={"game_id": self.game.id})

    def create_user(self):
        return User.objects.create_user(
            nickname="test_user",
            password="test1234",
            email="tset@test.com",
            phone_number="010-0000-0000",
        )

    def test_create_review_api_success(self):
        """
        리뷰 등록 성공 (201 Created)
        """
        self.client.force_authenticate(user=self.user)  # 로그인 처리
        payload = {
            "content": "그저그런 게임입니다.",
            "rating": 3
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "리뷰가 등록되었습니다.")
        self.assertTrue(Review.objects.filter(id=response.data["id"]).exists())

    def test_create_review_unauthorized(self):
        """
        비로그인 유저 요청 차단 (401 Unauthorized)
        """
        payload = {
            "content": "재미없어요",
            "rating": 1
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_review_invalid_rating(self):
        """
        별점 범위 초과 시 실패 (400 Bad Request)
        """
        # Given
        self.client.force_authenticate(user=self.user)
        payload = {
            "content": "완벽해요",
            "rating": 6  # 1~5
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # DRF 에러 응답 구조에 따라 'rating' 키 확인 (serializer.errors)
        self.assertIn("rating", response.data)

    def test_create_review_game_not_found(self):
        """
        없는 게임에 리뷰 등록 시 404 Not Found
        """
        self.client.force_authenticate(user=self.user)

        wrong_url = reverse("game_review_create", kwargs={"game_id": 99999})
        payload = {"content": "Ghost Game", "rating": 3}

        response = self.client.post(wrong_url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)