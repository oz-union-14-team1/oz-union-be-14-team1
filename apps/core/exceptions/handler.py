import logging
from typing import Any, Optional

from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("django")


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Optional[Response]:
    # 1. 핸들러 호출
    response = exception_handler(exc, context)

    # 2. 시스템 에러 (500)
    if response is None:
        logger.error(f"[System Error] {exc}", exc_info=True)
        return Response(
            {"error_detail": "서버 내부 오류가 발생했습니다.", "code": "server_error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 3. 에러 메시지 포맷 통일 (Detail -> Error Detail)
    if isinstance(response.data, dict):

        # 401 인증 에러 (로그인 안 함)
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            response.data = {"error_detail": "로그인이 필요한 서비스입니다."}

        # 유효성 검사 실패 (400)
        if isinstance(exc, ValidationError):
            view = context.get("view")
            # 뷰에 설정된 메시지 or 기본 메시지 가져오기
            message = getattr(
                view, "validation_error_message", "유효하지 않은 데이터입니다."
            )

            response.data = {"error_detail": message, "errors": response.data}

        # 그 외 모든 에러 (403, 404, 409 등)
        else:
            # 'detail' 키가 있으면 'error_detail'로 이름표 바꿔달기
            if "detail" in response.data:
                response.data = {"error_detail": str(response.data["detail"])}

            # 커스텀 예외에 code가 있다면 추가
            if hasattr(exc, "default_code"):
                response.data["code"] = exc.default_code

    return response
