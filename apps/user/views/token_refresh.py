from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema,OpenApiResponse

from apps.user.utils.tokens import TokenService
from apps.user.serializers.token_refresh import TokenRefreshRequestSerializer

class TokenRefreshWithBlacklistView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="토큰 재발급",
        description="refresh_token으로 access_token을 재발급합니다. 블랙리스트된 refresh_token은 거부합니다.",
        request=TokenRefreshRequestSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"access_token": {"type": "string"}},
                },
                description="재발급 성공",
            ),
            400: OpenApiResponse(description="refresh_token 누락"),
            401: OpenApiResponse(description="refresh_token 무효/블랙리스트"),
        },
    )

    def post(self, request):
        refresh = request.data.get("refresh_token") or request.COOKIES.get("refresh_token")
        if not refresh:
            return Response(
                {"detail": "refresh token 소실"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            access = TokenService().refresh_access_token(refresh)
        except TokenError as e:
            msg = str(e)
            if "Blacklisted" in msg:
                return Response({"detail": "blacklisted refresh token"}, status=401)
            return Response({"detail": "invalid refresh token"}, status=401)

        return Response({"access_token": access}, status=status.HTTP_200_OK)
