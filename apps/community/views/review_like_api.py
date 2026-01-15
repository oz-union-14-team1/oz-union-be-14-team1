from typing import cast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from apps.community.services.review.review_like_service import (
    add_review_like,
    remove_review_like,
)
from apps.user.models.user import User


class ReviewLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["좋아요"],
        summary="좋아요 투표 API",
    )
    def post(self, request: Request, review_id: int) -> Response:
        user = cast(User, request.user)

        total_likes = add_review_like(user=user, review_id=review_id)

        return Response(
            {
                "is_liked": True,
                "like_count": total_likes,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["좋아요"],
        summary="좋아요 투표 삭제 API",
    )
    def delete(self, request: Request, review_id: int) -> Response:
        user = cast(User, request.user)

        total_likes = remove_review_like(user=user, review_id=review_id)

        return Response(
            {
                "is_liked": False,
                "like_count": total_likes,
            },
            status=status.HTTP_200_OK,
        )
