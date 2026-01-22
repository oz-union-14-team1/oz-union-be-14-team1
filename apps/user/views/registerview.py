from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from apps.user.serializers.register import SignUpSerializer
from apps.user.utils.tokens import TokenService


class RegisterView(APIView):
    permission_classes = [AllowAny]

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
                "access_token": access_token,
            },
            status=status.HTTP_201_CREATED,
        )
