from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.community.pagination import ReviewPageNumberPagination
from apps.community.serializers.community_review_list import (
    CommunityReviewListSerializer,
)
from apps.community.services.community_review_service import get_community_review_all
from rest_framework.response import Response


class CommunityReviewListAPIView(APIView):
    """
    전체 리뷰 피드 조회
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=["커뮤니티"],
        summary="커뮤니티 리뷰 목록 조회 (장르 필터링)",
        responses=CommunityReviewListSerializer,
        parameters=[
            OpenApiParameter(
                name="genre",
                description="GenreListAPIView에서 조회된 '장르 명(Name)'을 전달하여 필터링",
                required=False,
                type=str,
                examples=[
                ],
            )
        ],
    )
    def get(self, request):
        # 1. 쿼리 파라미터 추출 (ex. ?genre=RPG)
        genre_name = request.query_params.get("genre")

        # 2. 서비스 호출 (slug 대신 name 전달)
        queryset = get_community_review_all(genre_name=genre_name)

        # 3. 페이지네이션
        paginator = ReviewPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            serializer = CommunityReviewListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CommunityReviewListSerializer(queryset, many=True)
        return Response(serializer.data, status=200)
