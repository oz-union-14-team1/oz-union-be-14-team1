from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.community.models.reviews import Review
from apps.game.models.game import Game

User = get_user_model()


class GameReviewAPITest(APITestCase):
    def setUp(self):
        """
        테스트 데이터 초기화
        """
        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.url = reverse("game_review_create", kwargs={"game_id": self.game.id})

    def create_user(self):
        return User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )

    def test_create_review_api_success(self):
        """
        리뷰 등록 성공 (201)
        """
        # Given: 유저 로그인 및 정상 데이터 준비
        self.client.force_authenticate(user=self.create_user())
        payload = {"content": "그저그런 게임입니다.", "rating": 3}

        # When: 리뷰 생성 API 호출
        response = self.client.post(self.url, payload)

        # Then: 201 응답 및 DB 저장 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "리뷰가 등록되었습니다.")
        self.assertTrue(Review.objects.filter(id=response.data["id"]).exists())

    def test_create_review_unauthorized(self):
        """
        비로그인 유저 요청 차단 (401 UnAuthorized)
        """
        # Given: 비로그인 상태 및 데이터 준비
        payload = {"content": "재미없어요", "rating": 1}

        # When: 리뷰 생성 API 호출
        response = self.client.post(self.url, payload)

        # Then: 401 에러 및 에러메세지 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "로그인이 필요한 서비스입니다.")

    def test_create_review_invalid_rating(self):
        """
        별점 범위 초과 시 실패 (400 Bad Request)
        """
        # Given: 잘못된 별점 데이터 준비
        self.client.force_authenticate(user=self.create_user())
        payload = {"content": "완벽해요", "rating": 6}

        # When: 리뷰 생성 API 호출
        response = self.client.post(self.url, payload)

        # Then: 400 에러 및 에러메세지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["errors"],
            {"rating": ["별점은 1에서 5 사이의 정수여야 합니다."]},
        )

    def test_create_review_invalid_content(self):
        """
        content 내용 없어서 실패 (400 Bad Request)
        """
        # Given: 내용이 빈 데이터 준비
        self.client.force_authenticate(user=self.create_user())
        payload = {"content": "", "rating": 3}

        # When: 리뷰 생성 API 호출
        response = self.client.post(self.url, payload)

        # Then: 400 에러 및 에러메세지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "이 필드는 필수 항목입니다.")

    def test_create_review_game_not_found(self):
        """
        없는 게임에 리뷰 등록 시 404
        """
        # Given: 존재하지 않는 게임 ID의 URL 생성
        self.client.force_authenticate(user=self.create_user())
        wrong_url = reverse("game_review_create", kwargs={"game_id": 99999})
        payload = {"content": "Ghost Game", "rating": 3}

        # When: 리뷰 생성 API 호출
        response = self.client.post(wrong_url, payload)

        # Then: 404 에러 및 에러 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 게임입니다.")
