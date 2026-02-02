import logging
import secrets

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.user.models import User
from apps.user.serializers.account_recovery import (
    FindAccountSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)

logger = logging.getLogger(__name__)


def _mask(value: str) -> str:
    value = value or ""
    length = len(value)

    if length <= 1:
        return value + "*"

    if length == 2:
        return value[0] + "*"

    return value[:2] + "***" + value[5:]

def mask_email(email: str) -> str:
    if "@" not in email:
        return _mask(email)

    local, domain = email.split("@", 1)
    return f"{_mask(local)}@{domain}"


def _generate_6bigit_code() -> str:
    return f"{secrets.randbelow(900000)+100000:06d}"

class FindAccountView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="계정 찾기",
        description="휴대폰 번호로 가입된 계정(identifier)을 찾아 마스킹하여 반환합니다.",
        request=FindAccountSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "exists": {"type": "boolean", "example": True},
                        "identifier": {"type": "string", "example": "my***"},
                        "message": {"type": "string", "example": "계정을 찾았습니다."},
                    },
                },
                description="계정 존재 여부 반환(존재하면 identifier 마스킹)",
            ),
            400: OpenApiResponse(description="잘못된 요청(필수값 누락/형식 오류)"),
        },
    )
    def post(self, request):
        serializer = FindAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"].strip()

        user = User.objects.filter(
            phone_number=phone_number,
            is_active=True,
        ).first()

        if not user:
            return Response(
                {"exists": False, "message": "일치하는 계정을 찾을 수 없습니다."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "exists": True,
                "identifier": _mask(user.email),
                "message": "계정을 찾았습니다.",
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="비밀번호 재설정 요청",
        description="identifier + 휴대폰 번호가 일치하면 6자리 인증 토큰을 발급(서버에 저장)하고 안내 메시지를 반환합니다.",
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "비밀번호 재설정 안내를 전송했습니다.",
                        }
                    },
                },
                description="요청 처리 완료(보안상 존재 여부와 관계없이 동일 응답)",
            ),
            400: OpenApiResponse(description="잘못된 요청(필수값 누락/형식 오류)"),
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"].strip()
        phone_number = serializer.validated_data["phone_number"].strip()

        user = User.objects.filter(
            email=identifier,
            phone_number=phone_number,
            is_active=True,
        ).first()

        code = None

        if user:
            ttl = getattr(settings, "VERIFICATION_TOKEN_TTL_SECONDS", 300)
            max_attempts = getattr(
                settings, "VERIFICATION_TOKEN_GENERATE_MAX_ATTEMPTS", 5
            )

            code = None

            for _ in range(max_attempts):
                candidate = _generate_6bigit_code()
                cache_key = f"password_reset:{candidate}"

                if cache.get(cache_key) is None:
                    cache.set(cache_key, user.id, timeout=ttl)
                    code = candidate
                    break

            if code is None:
                code = _generate_6bigit_code()
                cache.set(f"password_reset:{code}", user.id, timeout=ttl)

            logger.warning(
                "[비밀번호 리셋 코드] identifier=%s phone_number=%s code=%s ttl=%s",
                identifier,
                phone_number,
                code,
                ttl,
            )

        data = {"message": "비밀번호 재설정 안내를 전송했습니다."}
        if code:
            data["code"] = code

        return Response(data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="비밀번호 재설정 확정",
        description="6자리 인증 코드가 유효하면 새 비밀번호로 변경합니다.",
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "비밀번호가 성공적으로 변경되었습니다.",
                        }
                    },
                },
                description="비밀번호 변경 성공",
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "유효하지 않거나 만료된 토큰입니다.",
                        }
                    },
                },
                description="유효하지 않은 요청(토큰 만료/불일치/비밀번호 검증 실패 등)",
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        cache_key = f"password_reset:{code}"
        user_id = cache.get(cache_key)

        if not user_id:
            return Response(
                {"detail": "유효하지 않거나 만료된 인증 코드입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            return Response(
                {"detail": "유효하지 않은 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        cache.delete(cache_key)

        return Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )