from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from typing import cast

from apps.community.pagination import ReviewPageNumberPagination
from apps.community.serializers.review.review_create import ReviewCreateSerializer
from apps.community.serializers.review.review_list import ReviewListSerializer
from apps.community.services.review_create_service import create_review
from apps.community.services.review_list_service import get_review_list
from apps.user.models.user import User


class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    validation_error_message = "이 필드는 필수 항목입니다."

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


    def get(self, request, game_id):
        # 1. 서비스 레이어를 통해 QuerySet 가져오기
        queryset = get_review_list(game_id=game_id)

        # 2. 페이지네이션 객체 생성(APIView는 수동 호출 필요)
        paginator = ReviewPageNumberPagination()

        # 3. 쿼리셋을 현재 페이지에 맞게 자르기
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 4. 직렬화 (Serializer)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            # 5. 페이지네이션된 최종 응답 반환
            return paginator.get_paginated_response(serializer.data)

        # 만약 페이지네이션 설정이 꼬여서 page가 None이면 일반 리스트 반환 (예비책)
        serializer = ReviewListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
