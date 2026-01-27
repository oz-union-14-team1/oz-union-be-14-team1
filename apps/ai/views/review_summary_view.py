
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.ai.serializers.review_summary import SummaryRequestSerializer
from apps.ai.services.review_summary_service import ReviewSummaryService


class GameReviewSummaryAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["AI"],
        summary="게임 리뷰 AI 요약",
        description="게임 ID를 받아 AI가 생성한 리뷰 요약을 반환합니다.",
        request=SummaryRequestSerializer,  # 요청 파라미터 문서화
        responses={
            200: {
                "type": "object",
                "properties": {
                    "good_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["그래픽이 좋아요", "타격감이 찰져요"],
                    },
                    "bad_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["버그가 많아요"],
                    },
                    "total_review": {
                        "type": "string",
                        "example": "재밌지만 버그 수정이 필요함",
                    },
                },
            }
        },
    )
    def get(self, request, game_id):
        # 1. 입력 검증 (Serializer)
        input_serializer = SummaryRequestSerializer(data={"game_id": game_id})
        input_serializer.is_valid(raise_exception=True)

        # 2. 서비스 호출 (Service)
        service = ReviewSummaryService()

        result = service.get_summary(input_serializer.validated_data["game_id"])

        # 3. 성공 응답 (200 OK)
        return Response(result, status=status.HTTP_200_OK)
