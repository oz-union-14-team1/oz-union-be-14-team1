from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django.conf import settings
import jwt

from apps.user.serializers.login import LoginSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            detail = e.detail

            if isinstance(detail, dict) and "detail" not in detail:
                return Response(
                    {"error_detail": detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            error_message = detail.get("detail")

            if isinstance(error_message, list):
                error_message = error_message[0]

            if error_message == "탈퇴 신청한 계정입니다.":
                return Response(
                    {"error_detail": {"detail": error_message}},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {"error_detail": {"detail": error_message}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]

        payload = {
            "user_id": user.id,
            "email": user.email,
        }

        access_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return Response(
            {"access_token": access_token},
            status=status.HTTP_200_OK,
        )
