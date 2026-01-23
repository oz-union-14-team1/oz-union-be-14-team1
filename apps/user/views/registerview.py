from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from apps.user.serializers.register import SignUpSerializer, RegisterResponseSerializer
from apps.user.utils.tokens import TokenService


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="이메일/ 문자 인증을 완료한 사용자의 회원가입",
        request=SignUpSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="유효성 검증 실패"),
            409: OpenApiResponse(description="중복 회원"),
        },
        examples=[
            OpenApiExample(
                name="회원가입 요청 예시",
                value={
                    "email": "test@example.com",
                    "password": "Password1!",
                    "nickname": "김유진",
                    "name": "김본식",
                    "gender": "M",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="회원가입 성공 응답",
                value={
                    "detail": "회원가입이 완료되었습니다.",
                },
                response_only=True,
            ),
        ],
        auth=None,
    )
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            user = serializer.save()

            token_service = TokenService()
            _, access_token = token_service.create_token_pair(user=user)
        except ValidationError as e:
            return Response(
                {"error_detail": e.detail}, status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError:
            return Response(
                {"error_detail": "이미 중복된 회원가입 내역이 존재합니다."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {
                "detail": "회원가입이 완료되었습니다.",
            },
            status=status.HTTP_201_CREATED,
        )
