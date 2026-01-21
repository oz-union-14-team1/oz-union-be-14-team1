from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from django.urls import reverse

from apps.community.models.reviews import Review
from apps.community.models.comments import ReviewComment
from apps.game.models.game import Game

User = get_user_model()


class ReviewCommentAPITest(APITestCase):
    def setUp(self):
        # 1. 유저 생성
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        # 2. 게임 및 리뷰 생성
        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.review = Review.objects.create(
            user=self.user, game=self.game, content="재밌어요", rating=5
        )
        # 3. URL
        self.url = reverse("review_comments", kwargs={"review_id": self.review.id})

    def test_create_comment_success(self):
        """
        댓글 등록 성공 (201)
        """
        # Given: 로그인 및 데이터 준비
        self.client.force_authenticate(user=self.user)
        payload = {"content": "인정합니다."}

        # When: 댓글 작성 API 요청
        response = self.client.post(self.url, payload)

        # Then: 상태코드 201 및 응답 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["message"], "댓글이 등록되었습니다.")

        # Then: DB에 실제로 저장되었는지 확인
        comment_id = response.data["id"]
        self.assertTrue(ReviewComment.objects.filter(id=comment_id).exists())

        saved_comment = ReviewComment.objects.get(id=comment_id)
        self.assertEqual(saved_comment.content, "인정합니다.")
        self.assertEqual(saved_comment.review, self.review)
        self.assertEqual(saved_comment.user, self.user)

    def test_create_comment_unauthorized(self):
        """
        로그인하지 않은 유저가 요청 시 차단 (401)
        """
        # Given: 비로그인 상태 (force_authenticate 없음)
        payload = {"content": "로그인 안 하고 댓글 달기"}

        # When: API 요청
        response = self.client.post(self.url, payload)

        # Then: 401 에러 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "로그인이 필요한 서비스입니다.")

    def test_create_comment_invalid_data(self):
        """
        필수 항목(content) 누락 시 실패 (400)
        """
        # Given: 로그인 상태, 빈 content
        self.client.force_authenticate(user=self.user)
        payload = {"content": ""}

        # When: API 요청
        response = self.client.post(self.url, payload)

        # Then: 400 에러 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error_detail"], "이 필드는 필수 항목입니다.")

    def test_create_comment_review_not_found(self):
        """
        존재하지 않는 리뷰 ID에 댓글 작성 시도 (404)
        """
        # Given: 존재하지 않는 리뷰 ID로 URL 생성
        wrong_url = reverse("review_comments", kwargs={"review_id": 99999})
        self.client.force_authenticate(user=self.user)
        payload = {"content": "없는 리뷰에 댓글 달기"}

        # When: API 요청
        response = self.client.post(wrong_url, payload)

        # Then: 404 에러 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 리뷰입니다.")

    def test_create_comment_review_soft_deleted(self):
        """
        삭제된 리뷰에 댓글 작성 시도 (404)
        """
        # Given: 리뷰 삭제 처리 (is_deleted=True)
        self.review.is_deleted = True
        self.review.save()

        self.client.force_authenticate(user=self.user)
        payload = {"content": "삭제된 리뷰에 댓글 달기"}

        # When: API 요청
        response = self.client.post(self.url, payload)

        # Then: 404 에러 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 리뷰입니다.")
