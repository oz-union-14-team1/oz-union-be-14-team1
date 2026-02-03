from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from apps.game.services.importer import GameImportService
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["게임"],
    summary="관리자만 사용하는 게임 데이터 추가 api",
)
class GameImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            service = GameImportService()
            count = service.import_games()

            return Response(
                {
                    "message": f"{count}개의 새로운 게임이 추가되었습니다.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
