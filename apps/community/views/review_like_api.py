from rest_framework.views import APIView
from rest_framework.response import Response
from typing import cast
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.user.models.user import User
from apps.community.services.review_like_service import create_review_like


class ReviewLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, review_id: int) -> Response:
        user = cast(User, request.user)

        is_liked, total_likes = create_review_like(  # type: ignore
            user=user, review_id=review_id
        )

        return Response(
            {
                "message": "성공적으로 반영되었습니다.",
                "is_liked": is_liked,  # True면 하트 채우기, False면 비우기
                "like_count": total_likes,  # 숫자를 이 값으로 덮어씌우기
            },
            status=status.HTTP_200_OK,
        )
