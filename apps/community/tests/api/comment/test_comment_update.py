from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.community.models.reviews import Review
from apps.community.models.comments import ReviewComment
from apps.game.models.game import Game
from django.utils import timezone

User = get_user_model()


class ReviewCommentUpdateAPITest(APITestCase):
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

        self.comment = ReviewComment.objects.create(
            user=self.user, review=self.review, content="댓글입니다."
        )

        self.url = reverse(
            "review_comments_update", kwargs={"comment_id": self.comment.id}
        )

    def test_update_comment_success(self):
        """
        작성자 본인의 댓글 수정 성공
        """
        # Given: 작성자 본인 로그인 및 수정 데이터 준비
        self.client.force_authenticate(user=self.user)
        data = {"content": "수정된 댓글 내용입니다."}

        # When: 댓글 수정 API 호출
        response = self.client.put(self.url, data)

        # Then: 200 응답 및 DB 업데이트 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "수정된 댓글 내용입니다.")

    def test_update_comment_permission_denied(self):
        """
        다른 유저가 댓글 수정 시도 시 403
        """
        # Given: 작성자가 아닌 다른 유저로 로그인
        self.client.force_authenticate(user=self.other_user)
        data = {"content": "수정 시도"}

        # When: 댓글 수정 API 호출
        response = self.client.put(self.url, data)

        # Then: 403 반환 및 에러 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error_detail"], "작성자가 일치하지 않습니다.")

    def test_update_comment_unauthorized(self):
        """
        비로그인 유저가 수정 시도 시 401
        """
        # Given: 로그인하지 않음

        # When: 댓글 수정 API 호출
        response = self.client.put(self.url)

        # Then: 401 반환 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], "로그인이 필요한 서비스입니다.")

    def test_update_comment_not_found(self):
        """
        존재하지 않는 댓글 수정 시도 (404)
        """
        # Given: 작성자로 로그인했으나, 잘못된 댓글 ID 사용
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse("review_comments_update", kwargs={"comment_id": 99999})
        data = {"content": "New Content"}

        # When: 없는 댓글 수정 요청
        response = self.client.put(wrong_url, data)

        # Then: 404반환 확인
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error_detail"], "존재하지 않는 댓글입니다.")

    def test_update_comment_invalid_input(self):
        """
        유효하지 않은 데이터(빈 내용)로 수정 시도 시 400
        """
        # Given: 빈 content 전송
        self.client.force_authenticate(user=self.user)
        data = {"content": ""}

        # When: 댓글 수정 API 호출
        response = self.client.put(self.url, data)

        # Then: 400 에러 확인 및 에러 필드에 content가 있는지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data["errors"])
