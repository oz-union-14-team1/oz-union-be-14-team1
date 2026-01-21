from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from typing import cast
from rest_framework.response import Response
from apps.community.services.comment.comment_create_service import create_comment
from apps.user.models import User
from apps.community.serializers.comment.comment_create import (
    ReviewCommentCreateSerializer,
)
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


class ReviewCommentAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    validation_error_message = "이 필드는 필수 항목입니다."

    @extend_schema(
        tags=["댓글"],
        summary="댓글 등록 API",
        request=ReviewCommentCreateSerializer,
        responses={
            201: inline_serializer(
                name="ReviewCommentCreateSerializer",
                fields={
                    "id": serializers.IntegerField(),
                    "message": serializers.CharField(),
                },
            ),
        },
    )
    def post(self, request, review_id):
        # 1. 입력 데이터 검증
        serializer = ReviewCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 서비스 레이어 호출
        comment = create_comment(
            author=cast(User, request.user),
            review_id=review_id,
            validated_data=serializer.validated_data,
        )

        # 3. 응답 반환
        return Response(
            {"id": comment.id, "message": "댓글이 등록되었습니다."},
            status=status.HTTP_201_CREATED,
        )
