from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.community.pagination import ReviewPageNumberPagination
from apps.community.serializers.community_review_list import CommunityReviewListSerializer
from apps.community.services.community_review_service import get_community_review_all
from rest_framework.response import Response

class CommunityReviewListAPIView(APIView):
    """
    전체 리뷰 피드 조회
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=["커뮤니티"], summary="커뮤니티 목록 조회 API", responses=CommunityReviewListSerializer
    )
    def get(self, request):
        # 1. 커뮤니티 전용 서비스 호출
        queryset = get_community_review_all()

        # 2. 페이지네이션
        paginator = ReviewPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # 3. 커뮤니티 전용 Serializer 사용
        if page is not None:
            serializer = CommunityReviewListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CommunityReviewListSerializer(queryset, many=True)
        return Response(serializer.data, status=200)