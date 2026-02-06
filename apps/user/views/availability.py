from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.user.serializers.availability import (
    EmailAvailabilitySerializer,
    NicknameAvailabilitySerializer,
)


class EmailAvailabilityView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="이메일 중복 확인",
        description="회원가입 이메일 중복확인 버튼용 API",
        request=EmailAvailabilitySerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "available": {"type": "boolean", "example": True},
                        "message": {
                            "type": "string",
                            "example": "사용 가능한 이메일입니다.",
                        },
                    },
                }
            ),
            400: OpenApiResponse(description="중복/형식 오류"),
        },
        examples=[
            OpenApiExample(
                name="요청 예시",
                value={"email": "test@example.com"},
                request_only=True,
            )
        ],
        auth=None,
    )
    def post(self, request):
        serializer = EmailAvailabilitySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"available": True, "message": "사용 가능한 이메일입니다."},
            status=status.HTTP_200_OK,
        )


class NicknameAvailabilityView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="닉네임 중복 확인",
        description=(
            "회원가입/회원수정 닉네임 중복확인 버튼용 API. "
            "로그인 상태면 '기존 닉네임과 동일' 여부도 함께 검사합니다."
        ),
        request=NicknameAvailabilitySerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "available": {"type": "boolean", "example": True},
                        "message": {
                            "type": "string",
                            "example": "사용 가능한 닉네임입니다.",
                        },
                    },
                }
            ),
            400: OpenApiResponse(description="중복/형식 오류"),
        },
        examples=[
            OpenApiExample(
                name="요청 예시",
                value={"nickname": "양민순"},
                request_only=True,
            )
        ],
        auth=None,
    )
    def post(self, request):
        serializer = NicknameAvailabilitySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"available": True, "message": "사용 가능한 닉네임입니다."},
            status=status.HTTP_200_OK,
        )
