from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.user.serializers.login import LoginSerializer
from apps.user.utils.tokens import TokenService


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 로그인",
        description="이메일과 비밀번호로 로그인해서 access token을 발급합니다.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        }
                    },
                },
                description="로그인 성공",
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            403: OpenApiResponse(description="탈퇴 신청한 계정"),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token_service = TokenService()
        refresh_token,access_token = token_service.create_token_pair(user=user)

        response = Response(
            {"access_token": access_token},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(key="refresh_token", value=refresh_token)

        return response
