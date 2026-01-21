from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ReviewCommentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    validation_error_message = "이 필드는 필수 항목입니다."