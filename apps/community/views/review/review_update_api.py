from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.permissions.review_permissions import IsReviewAuthor
from apps.community.serializers.review.review_create import ReviewCreateSerializer
from apps.community.services.review.review_delete_service import delete_review
from apps.community.services.review.review_update_service import update_review

from apps.community.models.reviews import Review


class ReviewUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsReviewAuthor]
    validation_error_message = "이 필드는 필수 항목입니다."

    def get_review(self, request, review_id) -> Review:
        """
        리뷰 조회 및 권한 검증을 수행
        """
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            raise ReviewNotFound()

        # 권한 검사
        self.check_object_permissions(request, review)

        return review

    @extend_schema(
        tags=["리뷰"],
        summary="리뷰 수정 API",
        request=ReviewCreateSerializer,
        responses=ReviewCreateSerializer,
    )
    def patch(self, request, review_id):
        self.validation_error_message = "유효하지 않은 수정 요청입니다."
        # 1. 조회 & 검증
        review = self.get_review(request, review_id)

        # 2. 데이터 검증
        serializer = ReviewCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # 3. 서비스 호출
        updated_review = update_review(
            review=review, validated_data=serializer.validated_data
        )
        return Response(
            ReviewCreateSerializer(updated_review).data, status=status.HTTP_200_OK
        )

    @extend_schema(tags=["리뷰"], summary="리뷰 삭제 API")
    def delete(self, request, review_id):
        # 1. 조회 & 검증
        review = self.get_review(request, review_id)

        # 2. 서비스 호출
        delete_review(review=review)

        return Response(
            {"message": "리뷰가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
