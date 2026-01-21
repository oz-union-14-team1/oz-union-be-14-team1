from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.community.services.comment.comment_create_service import create_comment
from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models.reviews import Review
from apps.community.models.comments import ReviewComment
from apps.game.models.game import Game

User = get_user_model()


class ReviewCommentServiceTest(TestCase):
    def setUp(self):
        # 1. 유저 및 데이터 준비
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

    def test_create_comment_service_success(self):
        """
        서비스 로직을 통한 댓글 생성 성공
        """
        # Given
        data = {"content": "서비스 테스트 중입니다."}

        # When: 서비스 함수 직접 호출
        comment = create_comment(
            author=self.user,
            review_id=self.review.id,
            validated_data=data
        )

        # Then: 반환된 객체 및 DB 저장 검증
        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.content, "서비스 테스트 중입니다.")
        self.assertEqual(comment.review, self.review)
        self.assertEqual(comment.user, self.user)

        # 실제 DB 카운트 확인
        self.assertEqual(ReviewComment.objects.count(), 1)

    def test_create_comment_fail_review_not_found(self):
        """
        존재하지 않는 리뷰 ID로 요청 시 ReviewNotFound 예외 발생
        """
        # Given
        invalid_id = 99999
        data = {"content": "제발 실패"}

        # When & Then: 예외 발생 확인
        with self.assertRaises(ReviewNotFound):
            create_comment(
                author=self.user,
                review_id=invalid_id,
                validated_data=data
            )

    def test_create_comment_fail_soft_deleted_review(self):
        """
        삭제된 리뷰에 댓글 작성 시도 시 예외 발생
        """
        # Given: 리뷰 삭제 처리
        self.review.is_deleted = True
        self.review.save()

        data = {"content": "삭제된 리뷰입니다."}

        # When & Then: 서비스 로직에서 필터링되어 ReviewNotFound가 떠야 함
        with self.assertRaises(ReviewNotFound):
            create_comment(
                author=self.user,
                review_id=self.review.id,
                validated_data=data
            )

