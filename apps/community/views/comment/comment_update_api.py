from apps.community.exceptions.review_exceptions import CommentNotFound
from apps.community.models import ReviewComment
from apps.community.permissions.review_permissions import IsReviewAuthor
from apps.community.services.comment.comment_delete_service import delete_comment
from apps.community.services.comment.comment_update_service import update_comment
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.serializers.comment.comment_create import (
    ReviewCommentCreateSerializer,
)


class ReviewCommentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsReviewAuthor]
    validation_error_message = "이 필드는 필수 항목입니다."

    def get_comment(self, request, comment_id) -> ReviewComment:
        """
        댓글 조회 및 권한 검증을 수행
        """
        try:
            comment = ReviewComment.objects.get(id=comment_id)
        except ReviewComment.DoesNotExist:
            raise CommentNotFound()

        # 권한 검사
        self.check_object_permissions(request, comment)

        return comment

    @extend_schema(
        tags=["댓글"],
        summary="댓글 수정 API",
        request=ReviewCommentCreateSerializer,
        responses={200: ReviewCommentCreateSerializer},
    )
    def put(self, request, comment_id):
        self.validation_error_message = "유효하지 않은 수정 요청입니다."
        # 1. 조회 & 검증
        comment = self.get_comment(request, comment_id)

        # 2. 데이터 검증
        serializer = ReviewCommentCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 4. 서비스 레이어 호출
        comment = update_comment(
            comment=comment, validated_data=serializer.validated_data
        )

        # 4. 수정된 데이터 반환
        return Response(
            ReviewCommentCreateSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(tags=["댓글"], summary="댓글 삭제 API")
    def delete(self, request, comment_id):
        # 1. 조회 & 검증
        comment = self.get_comment(request, comment_id)

        # 2. 서비스 레이어 호출
        delete_comment(comment=comment)

        return Response(
            {"message": "댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
