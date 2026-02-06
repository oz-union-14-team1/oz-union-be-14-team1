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
    CodeVerifySerializer,
    CodeSendSerializer,
)

# [추가] SMS 발송 유틸리티 import
from apps.user.utils.sender import SMSSender

logger = logging.getLogger(__name__)


def _mask(value: str) -> str:
    value = value or ""
    length = len(value)

    if length <= 1:
        return value + "*"

    elif length == 2:
        return value[0] + "*"

    elif length == 3:
        return value[0] + "*" + value[-1]

    else:
        return value[:2] + "*" * (length - 4) + value[-2:]


def mask_email(email: str) -> str:
    if "@" not in email:
        return _mask(email)

    local, domain = email.split("@", 1)
    return f"{_mask(local)}@{domain}"


def _generate_6bigit_code() -> str:
    return f"{secrets.randbelow(900000) + 100000:06d}"


class FindAccountView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="계정 찾기",
        description="휴대폰 인증을 통과한 phone_number로 가입된 계정을 마스킹하여 반환합니다.",
        request=FindAccountSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "exists": {"type": "boolean", "example": True},
                        "identifier": {
                            "type": "string",
                            "example": "my***@example.com",
                        },
                        "message": {"type": "string", "example": "계정을 찾았습니다."},
                    },
                },
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "휴대폰 인증이 필요합니다.",
                        }
                    },
                }
            ),
        },
    )
    def post(self, request):
        serializer = FindAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        if not cache.get(f"verify:ok:find_account:{phone_number}"):
            return Response(
                {"detail": "휴대폰 인증이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(phone_number=phone_number, is_active=True).first()
        if not user:
            cache.delete(f"verify:ok:find_account:{phone_number}")
            cache.delete(f"verify:sms:find_account:{phone_number}")
            return Response(
                {"exists": False, "message": "일치하는 계정을 찾을 수 없습니다."},
                status=status.HTTP_200_OK,
            )

        cache.delete(f"verify:ok:find_account:{phone_number}")
        cache.delete(f"verify:sms:find_account:{phone_number}")

        return Response(
            {
                "exists": True,
                "identifier": mask_email(user.email),
                "message": "계정을 찾았습니다.",
            },
            status=status.HTTP_200_OK,
        )


class CodeSendView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="인증번호 전송",
        description="""phone_number로 6자리 인증번호를 생성해 캐시에 저장합니다. purpose로 용도를 구분합니다.""",
        request=CodeSendSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "인증번호를 전송했습니다.",
                        },
                        "code": {"type": "string", "example": "123456"},
                    },
                }
            )
        },
    )
    def post(self, request):
        serializer = CodeSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        purpose = serializer.validated_data.get("purpose", "password_reset")

        ttl = getattr(settings, "VERIFICATION_DEFAULT_TTL_SECONDS", 300)
        code = _generate_6bigit_code()

        cache.set(f"verify:sms:{purpose}:{phone_number}", code, timeout=ttl)

        # [수정] 실제 문자 발송 (배포 환경에서도 문자로 확인 가능)
        try:
            SMSSender.send_verification_code(phone_number, code)
        except Exception as e:
            logger.error(f"[SMS_SEND_FAIL] phone={phone_number} error={e}")

        data = {"message": "인증번호를 전송했습니다."}

        # [수정] 테스트 통과를 위해 settings.DEBUG 조건 복구
        # (배포 환경에서는 API 응답에 code가 포함되지 않아야 테스트가 성공함)
        if settings.DEBUG:
            data["code"] = code
            logger.warning(
                "[CODE_SEND] purpose=%s phone=%s code=%s ttl=%s",
                purpose,
                phone_number,
                code,
                ttl,
            )

        return Response(data, status=status.HTTP_200_OK)


class CodeVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="인증번호 확인",
        description="phone_number + code가 일치하면 인증 성공. purpose로 용도를 구분합니다.",
        request=CodeVerifySerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "인증이 성공하였습니다.",
                        }
                    },
                }
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "인증번호가 올바르지 않거나 만료되었습니다.",
                        }
                    },
                }
            ),
        },
    )
    def post(self, request):
        # [수정] CodeSendView로 덮어씌워진 로직을 원래 CodeVerify 로직으로 복구
        serializer = CodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data.get("purpose", "password_reset")

        sms_key = f"verify:sms:{purpose}:{phone_number}"
        saved_code = cache.get(sms_key)

        # 인증번호 불일치 체크 (400 에러)
        if not saved_code or saved_code != code:
            return Response(
                {"detail": "인증번호가 올바르지 않거나 만료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ttl = getattr(settings, "VERIFICATION_DEFAULT_TTL_SECONDS", 300)

        # 인증 성공 처리
        cache.set(f"verify:ok:{purpose}:{phone_number}", True, timeout=ttl)
        cache.delete(sms_key)

        return Response(
            {"message": "인증이 성공하였습니다."}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    # ... (기존 코드 유지)
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="비밀번호 재설정 요청",
        description="password_reset 인증 통과 + code 확인 후 reset_token을 발급하고, 토큰은 HttpOnly 쿠키로만 설정합니다.",
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "비밀번호 재설정 요청이 확인되었습니다.",
                        }
                    },
                }
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "휴대폰 인증이 필요합니다.",
                        }
                    },
                }
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = (serializer.validated_data["identifier"] or "").strip()
        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        if not cache.get(f"verify:ok:password_reset:{phone_number}"):
            return Response(
                {"detail": "휴대폰 인증이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        saved_code = cache.get(f"verify:sms:password_reset:{phone_number}")
        if not saved_code or saved_code != code:
            return Response(
                {"detail": "인증번호가 올바르지 않거나 만료되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            email=identifier,
            phone_number=phone_number,
            is_active=True,
        ).first()
        if not user:
            return Response(
                {"detail": "일치하는 계정을 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ttl = getattr(settings, "VERIFICATION_DEFAULT_TTL_SECONDS", 300)
        reset_token = secrets.token_urlsafe(32)
        cache.set(f"pw_reset:token:{reset_token}", user.id, timeout=ttl)

        # 인증 관련 키 1회용 처리
        cache.delete(f"verify:ok:password_reset:{phone_number}")
        cache.delete(f"verify:sms:password_reset:{phone_number}")

        resp = Response(
            {"message": "비밀번호 재설정 요청이 확인되었습니다."},
            status=status.HTTP_200_OK,
        )

        resp.set_cookie(
            key="pw_reset_token",
            value=reset_token,
            max_age=ttl,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/api/v1/user/password/reset/",
        )
        return resp


class PasswordResetConfirmView(APIView):
    # ... (기존 코드 유지)
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["회원관리"],
        summary="비밀번호 재설정 확정",
        description="쿠키가 유효하면 새 비밀번호로 변경합니다.",
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
                }
            ),
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "유효하지 않거나 만료된 인증입니다.",
                        }
                    },
                }
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_token = request.COOKIES.get("pw_reset_token")
        if not reset_token:
            return Response(
                {"detail": "인증 정보가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token_key = f"pw_reset:token:{reset_token}"
        user_id = cache.get(f"pw_reset:token:{reset_token}")
        if not user_id:
            return Response(
                {"detail": "유효하지 않거나 만료된 인증입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            cache.delete(token_key)
            resp = Response(
                {"detail": "유효하지 않은 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            resp.delete_cookie("pw_reset_token", path="/api/v1/user/password/reset/")
            return resp

        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save(update_fields=["password"])

        cache.delete(token_key)

        resp = Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )

        resp.delete_cookie("pw_reset_token", path="/api/v1/user/password/reset/")
        return resp
