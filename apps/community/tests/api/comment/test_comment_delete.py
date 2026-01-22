from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.community.models import Review, ReviewComment
from apps.game.models.game import Game
from django.utils import timezone

User = get_user_model()


class ReviewCommentDeleteAPITest(APITestCase):
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
            user=self.user, game=self.game, content="삭제 예정", rating=5
        )

        self.comment = ReviewComment.objects.create(
            review=self.review,
            user=self.user,
            content="삭제될 댓글입니다.",
            is_deleted=False,
        )

        self.url = reverse(
            "review_comments_update", kwargs={"comment_id": self.comment.id}
        )

    def test_delete_comment_success(self):
        """
        본인이 작성한 댓글 삭제 성공 (is_deleted=True)
        """
        # Given: 작성자 본인 로그인
        self.client.force_authenticate(user=self.user)

        # When: 댓글 삭제 요청
        response = self.client.delete(self.url)

        # Then: 204 No Content / is_deleted=True
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_permission_denied(self):
        """
        타인이 댓글 삭제 시도 시 실패 (403)
        """
        # Given: 작성자가 아닌 다른 유저로 로그인
        self.client.force_authenticate(user=self.other_user)

        # When: 남의 리뷰 삭제 요청
        response = self.client.delete(self.url)

        # Then: 403 Forbidden 반환 / 데이터 삭제 여부 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_deleted)
        self.assertEqual(response.data["error_detail"], "작성자가 일치하지 않습니다.")

    def test_delete_comment_unauthorized(self):
        """
        비로그인 유저가 삭제 시도 시 차단 (401)
        """
        # Given: 로그인하지 않은 상태 (force_authenticate 없음)

        # When: 댓글 삭제 요청
        response = self.client.delete(self.url)

        # Then: 401 Unauthorized 반환 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "로그인이 필요한 서비스입니다.")

    def test_delete_comment_not_found(self):
        """
        존재하지 않는 리뷰 삭제 시도 (404)
        """
        # Given: 작성자로 로그인했으나, 잘못된 리뷰 ID 준비
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse("review_comments_update", kwargs={"comment_id": 99999})

        # When: 없는 리뷰 삭제 요청
        response = self.client.delete(wrong_url)

        # Then: 404 Not Found 반환 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 댓글입니다.")
