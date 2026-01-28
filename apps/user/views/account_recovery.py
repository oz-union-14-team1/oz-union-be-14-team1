import secrets

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.user.models import User
from apps.user.serializers.account_recovery import (
    FindAccountSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)


def _mask(value: str) -> str:
    value = value or ""
    if len(value) <= 2:
        return value[0] + "*" if value else ""
    return value[:2] + "***" + value[-1]


class FindAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FindAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"].strip()
        phone_number = serializer.validated_data["phone_number"].strip()

        user = User.objects.filter(
            email=identifier,
            phone_number=phone_number,
            is_active=True,
        ).first()

        if not user:
            return Response({"exists": False}, status=status.HTTP_200_OK)

        return Response(
            {"exists": True, "nickname": _mask(user.nickname)},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

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

        if user:
            token = secrets.token_urlsafe(settings.VERIFICATION_TOKEN_BYTES)
            ttl = getattr(settings, "VERIFICATION_TOKEN_TTL_SECONDS", None)

            if ttl is None:
                ttl = getattr(settings, "VERIFICATION_DEFAULT_TTL_SECONDS", 300)

            cache.set(f"password_reset:{token}", user.id, timeout=ttl)

        return Response(
            {"message": "비밀번호 재설정 안내를 전송했습니다."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        cache_key = f"password_reset:{token}"
        user_id = cache.get(cache_key)

        if not user_id:
            return Response(
                {"detail": "유효하지 않거나 만료된 토큰입니다."},
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
