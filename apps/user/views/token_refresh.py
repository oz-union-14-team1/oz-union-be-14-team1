from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.user.utils.tokens import TokenService
from apps.user.serializers.token_refresh import TokenRefreshRequestSerializer


class TokenRefreshWithBlacklistView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
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
        refresh = request.data.get("refresh_token") or request.COOKIES.get(
            "refresh_token"
        )
        if not refresh:
            return Response(
                {"detail": "refresh token 소실"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            access = TokenService().refresh_access_token(refresh)
        except AuthenticationFailed as e:
            codes = e.get_codes()
            flat = (
                {codes}
                if isinstance(codes, str)
                else set(codes) if isinstance(codes, list) else set()
            )
            if "token_Blacklisted" in flat:
                return Response(
                    {"detail": "blacklisted refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {"detail", "unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        except TokenError:
            return Response(
                {"detail": "invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({"access_token": access}, status=status.HTTP_200_OK)
