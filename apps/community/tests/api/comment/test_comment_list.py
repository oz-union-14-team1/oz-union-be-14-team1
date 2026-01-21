from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from django.urls import reverse

from apps.community.models.reviews import Review
from apps.community.models.comments import ReviewComment
from apps.game.models.game import Game

User = get_user_model()


class ReviewCommentListAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.commenter = User.objects.create_user(
            email="test1@test.com",
            password="test1234",
            nickname="test_user1",
            phone_number="010-0000-0001",
        )

        self.game = Game.objects.create(name="Test Game", released_at=timezone.now())
        self.review = Review.objects.create(
            user=self.user, game=self.game, content="재밌어요", rating=5
        )

        for i in range(3):
            ReviewComment.objects.create(
                user=self.commenter,
                review=self.review,
                content=f"댓글 내용 {i}",
            )

        self.url = reverse("review_comments", kwargs={"review_id": self.review.id})

    def test_get_review_comments_success(self):
        """
        리뷰 상세 및 댓글 목록 조회 성공 (200)
        """
        # Given: 로그인 하지 않은 상태 (조회는 가능해야 함)

        # When: 조회 API 호출
        response = self.client.get(self.url)

        # Then: 상태코드 200 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Then: 응답 데이터 구조 검증 (리뷰 정보 + comments 리스트)
        self.assertEqual(response.data["id"], self.review.id)
        self.assertEqual(response.data["content"], self.review.content)
        self.assertIn("comments", response.data)

        # Then: 댓글 개수 및 내용 검증
        comments = response.data["comments"]
        self.assertEqual(len(comments), 3)

    def test_get_review_comments_review_not_found(self):
        """
        존재하지 않는 리뷰 조회 시 404
        """
        # Given: 존재하지 않는 리뷰
        wrong_url = reverse("review_comments", kwargs={"review_id": 99999})

        # When: 조회 API 호출
        response = self.client.get(wrong_url)

        # Then: 404 에러 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 리뷰입니다.")

    def test_get_review_comments_soft_deleted_review(self):
        """
        삭제된 리뷰(is_deleted=True) 조회 시 404
        """
        # Given: 리뷰 삭제 처리
        self.review.is_deleted = True
        self.review.save()

        # When: 조회 API 호출
        response = self.client.get(self.url)

        # Then: 404 에러 확인 (삭제된 리뷰는 조회되지 않아야 함)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 리뷰입니다.")