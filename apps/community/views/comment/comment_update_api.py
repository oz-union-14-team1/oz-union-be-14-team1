from typing import cast

from apps.community.services.comment.comment_update_service import update_comment
from apps.user.models import User
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.serializers.comment.comment_create import ReviewCommentCreateSerializer


class ReviewCommentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    validation_error_message = "이 필드는 필수 항목입니다."

    @extend_schema(
        tags=["댓글"],
        summary="댓글 수정 API",
        request=ReviewCommentCreateSerializer,
        responses={200: ReviewCommentCreateSerializer},
    )
    def put(self, request, comment_id):
        self.validation_error_message = "유효하지 않은 수정 요청입니다."

        # 1. 수정할 데이터 검증
        serializer = ReviewCommentCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 2. 유저 타입 캐스팅 (Type Hinting)
        user = cast(User, request.user)

        # 3. 서비스 레이어 호출 (존재 여부 및 권한 검증 포함)
        comment = update_comment(
            user=user,
            comment_id=comment_id,
            validated_data=serializer.validated_data,
        )

        # 4. 수정된 데이터 반환
        return Response(
            ReviewCommentCreateSerializer(comment).data,
            status=status.HTTP_200_OK,
        )
