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
        # Given: 작성자 본인 로그인
        self.client.force_authenticate(user=self.user)

        # When: "좋아요" 등록 API 호출
        response = self.client.post(self.url)

        # Then: 201 응답
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["like_count"], 1)

        # Then: 한 번 더 요청해도 개수가 늘어나지 않은지 확인
        response_2 = self.client.post(self.url)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.data["like_count"], 1)

    def test_delete_review_like_success(self):
        """
        좋아요 취소 성공 (200 OK)
        """
        # Given: 작성자 본인 로그인 및 "좋아요" 등록 API 호출
        self.client.force_authenticate(user=self.user)

        self.client.post(self.url)

        # When: "좋아요" 삭제 API 호출
        response = self.client.delete(self.url)

        # Then: 200 응답 및 like_count 개수 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["like_count"], 0)

    def test_api_unauthorized(self):
        """
        비로그인 유저 요청 시 차단 (401 Unauthorized)
        """
        # Given: 로그인하지 않은 상태 (force_authenticate 없음)

        # When: "좋아요" 등록 API 호출
        response_post = self.client.post(self.url)

        # Then: 등록 401 Unauthorized 반환 확인 및 에러메세지 확인
        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response_post.data["error_detail"], "로그인이 필요한 서비스입니다."
        )

        # Then: 삭제 401 Unauthorized 반환 확인 및 에러메세지 확인
        response_delete = self.client.delete(self.url)
        self.assertEqual(response_delete.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response_delete.data["error_detail"], "로그인이 필요한 서비스입니다."
        )

    def test_api_not_found(self):
        """
        존재하지 않는 리뷰에 요청 시 404 Not Found
        """
        # Given: 작성자 본인 로그인 및 잘못된 데이터 준비
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse("review_like", kwargs={"review_id": 99999})

        # When: "좋아요" 등록 API 호출
        response_post = self.client.post(wrong_url)

        # Then: 등록 404 Not Found 반환 확인 및 에러메세지 확인
        self.assertEqual(response_post.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response_post.data["error_detail"], "존재하지 않는 리뷰입니다."
        )

        # Then: 삭제 404 Not Found 반환 확인 및 에러메세지 확인
        response_delete = self.client.delete(wrong_url)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response_delete.data["error_detail"], "존재하지 않는 리뷰입니다."
        )
