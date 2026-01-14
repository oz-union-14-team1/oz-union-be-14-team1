from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.game.models.game import Game
from apps.community.models.reviews import Review

User = get_user_model()


class GameReviewListAPITest(APITestCase):
    def setUp(self):
        """
        테스트 데이터 초기화
        - 유저 생성
        - 게임 생성
        - 리뷰 15개 생성 (페이지네이션 테스트용, page_size=10 가정)
        """
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.url = reverse("game_review_create", kwargs={"game_id": self.game.id})

        # 15개의 리뷰 생성(auto_now_add=True이므로 생성 순서대로 저장됨)
        for i in range(15):
            Review.objects.create(
                user=self.user, game=self.game, content=f"최고에요 {i}", rating=5
            )

    def test_get_reviews_success(self):
        """
        리뷰 목록 조회 성공 (200)
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지네이션 응답 구조 확인 (count, next, previous, results)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

        # 전체 개수는 15개
        self.assertEqual(response.data["count"], 15)

        # 1페이지는 10개 반환 (ReviewPageNumberPagination.page_size = 10)
        self.assertEqual(len(response.data["results"]), 10)

    def test_get_reviews_pagination_second_page(self):
        """
        리뷰 목록 조회 페이지네이션 (2페이지)
        """
        response = self.client.get(self.url, {"page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2페이지는 남은 5개 반환(10개는 1페이지)
        self.assertEqual(len(response.data["results"]), 5)
        # 다음 페이지는 없어야 함 (None)
        self.assertIsNone(response.data["next"])

    def test_get_reviews_invalid_page_type(self):
        """
        잘못된 페이지 번호 타입 요청 - 400 Bad Request
        """
        response = self.client.get(self.url, {"page": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data["error_detail"], "유효하지 않은 조회 요청입니다."
        )
        self.assertIn("page는 정수여야 합니다.", str(response.data["errors"]))

    def test_get_reviews_invalid_page_zero(self):
        """
        잘못된 페이지 번호 범위 요청 (0페이지) - 400 Bad Request
        """
        response = self.client.get(self.url, {"page": 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error_detail"], "유효하지 않은 조회 요청입니다."
        )
        self.assertIn("page는 1 이상이어야 합니다.", str(response.data["errors"]))

    def test_get_reviews_page_out_of_range(self):
        """
        페이지 범위를 벗어난 요청 - 200 OK (빈 리스트 반환)
        """
        response = self.client.get(self.url, {"page": 999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 빈 리스트 반환 확인
        self.assertEqual(len(response.data["results"]), 0)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_get_reviews_empty_game(self):
        """
        리뷰가 없는 게임 조회 - 200 OK (빈 리스트)
        """
        new_game = Game.objects.create(name="New Game", released_at=timezone.now())
        url = reverse("game_review_create", kwargs={"game_id": new_game.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_get_reviews_non_existent_game(self):
        """
        존재하지 않는 게임 ID로 조회 - 200 OK (빈 리스트)
        """
        url = reverse("game_review_create", kwargs={"game_id": 99999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)
