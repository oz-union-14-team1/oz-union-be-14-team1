from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from typing import cast
from apps.community.serializers.review_create import ReviewCreateSerializer
from apps.community.services.review_create_service import create_review
from apps.user.models.user import User


class GameReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        # 1. 입력 데이터 검증
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 유저 타입 캐스팅 (Type Hinting)
        user = cast(User, request.user)

        # 3. 서비스 레이어 호출
        review = create_review(
            author=user,
            game_id=game_id,
            validated_data=serializer.validated_data,
        )

        # 4. 응답 반환
        return Response(
            {"id": review.id, "message": "리뷰가 등록되었습니다."},
            status=status.HTTP_201_CREATED,
        )


#    def get(self, request):
#     ...
