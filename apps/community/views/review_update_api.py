from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.serializers.review.review_update import ReviewUpdateSerializer
from apps.community.services.review.review_update_service import update_review
from apps.user.models.user import User

class ReviewUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    validation_error_message = "이 필드는 필수 항목입니다."

    @extend_schema(
        tags=["리뷰"],
        summary="리뷰 수정 API",
        request=ReviewUpdateSerializer,
        responses=ReviewUpdateSerializer,
    )

    def patch(self, request, review_id):
        self.validation_error_message = "유효하지 않은 수정 요청입니다."

        # 1. 수정할 데이터 검증
        serializer = ReviewUpdateSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        # 2. 유저 타입 캐스팅 (Type Hinting)
        user = cast(User, request.user)

        # 3. 서비스 레이어 호출 (존재 여부 및 권한 검증 포함)
        review = update_review(
            user=user,
            review_id=review_id,
            validated_data=serializer.validated_data,
        )

        # 4. 수정된 데이터 반환
        return Response(
            ReviewUpdateSerializer(review).data,
            status=status.HTTP_200_OK,
        )
