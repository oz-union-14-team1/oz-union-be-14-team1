from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, inline_serializer
from typing import cast
from rest_framework import serializers
from apps.community.pagination import ReviewPageNumberPagination
from apps.community.serializers.review.review_create import ReviewCreateSerializer
from apps.community.serializers.review.review_list import ReviewListSerializer
from apps.community.services.review.review_create_service import create_review
from apps.community.services.review.review_list_service import (
    get_review_list,
    get_my_review_list,
)
from apps.user.models.user import User


class ReviewPaginationMixin:
    """
    리뷰 목록 페이지네이션 중복 로직을 처리하는 Mixin 클래스
    """

    def get_paginated_response(self, request, queryset, serializer_class):
        # 1. 페이지네이션 객체 생성
        paginator = ReviewPageNumberPagination()

        # 2. 쿼리셋을 현재 페이지에 맞게 자르기
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 3. 직렬화 (Serializer)
        if page is not None:
            serializer = serializer_class(page, many=True)
            # 4. 페이지네이션된 최종 응답 반환
            return paginator.get_paginated_response(serializer.data)

        # 만약 페이지네이션 설정이 꼬여서 page가 None이면 일반 리스트 반환 (예비책)
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewAPIView(APIView, ReviewPaginationMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]

    validation_error_message = "이 필드는 필수 항목입니다."

    @extend_schema(
        tags=["리뷰"],
        summary="리뷰 등록 API",
        request=ReviewCreateSerializer,
        responses={
            201: inline_serializer(
                name="ReviewCreateResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "message": serializers.CharField(),
                },
            ),
        },
    )
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

    @extend_schema(
        tags=["리뷰"], summary="리뷰 목록 조회 API", responses=ReviewListSerializer
    )
    def get(self, request, game_id):
        self.validation_error_message = "유효하지 않은 조회 요청입니다."
        # 1. 서비스 레이어를 통해 QuerySet 가져오기
        queryset = get_review_list(game_id=game_id)

        # 2. Mixin의 공통 메서드를 사용하여 응답 반환
        return self.get_paginated_response(
            request=request, queryset=queryset, serializer_class=ReviewListSerializer
        )


class MyReviewListAPIView(APIView, ReviewPaginationMixin):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["리뷰"],
        summary="내가 작성한 리뷰 목록 조회 API",
        responses=ReviewListSerializer,
    )
    def get(self, request):
        # 1. 서비스 레이어를 통해 QuerySet 가져오기
        queryset = get_my_review_list(user=request.user)

        # 2. Mixin의 공통 메서드를 사용하여 응답 반환
        return self.get_paginated_response(
            request=request, queryset=queryset, serializer_class=ReviewListSerializer
        )
