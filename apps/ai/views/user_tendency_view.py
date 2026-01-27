from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.ai.services.user_tendency import UserTendencyService


class UserTendencyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["AI"],
        summary="유저 성향 분석 (10자 이내)",
        description="유저의 선호 장르/태그를 기반으로 AI가 분석한 게이머 성향을 반환합니다.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "tendency": {"type": "string", "example": "낭만파 RPG 전사"}
                }
            }
        }
    )
    def get(self, request):
        # 1. 서비스 호출
        service = UserTendencyService()
        result = service.get_or_create_tendency(request.user)

        # 2. 결과 반환
        return Response(result, status=status.HTTP_200_OK)