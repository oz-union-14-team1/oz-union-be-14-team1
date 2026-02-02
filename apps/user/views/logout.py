from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.user.utils.tokens import TokenService


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["회원관리"],
        summary="로그아웃",
        description="Refresh Token , Access Token 을 블랙리스트 처리하고 쿠키를 삭제합니다.",
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"detail": {"type": "string"}},
                },
                description="로그아웃 성공",
            )
        },
    )
    def post(self, request):
        svc = TokenService()

        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            svc.blacklist(refresh_token)

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            access_token = auth.split(" ", 1)[1].strip()
            svc.blacklist_access(access_token)

        response = Response(
            {"detail": "로그아웃 되었습니다."}, status=status.HTTP_200_OK
        )
        response.delete_cookie("refresh_token", path="/")
        return response
