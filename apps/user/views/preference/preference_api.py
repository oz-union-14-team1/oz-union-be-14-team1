from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.user.serializers.preference.preference_create import UserPreferenceSerializer
from apps.user.serializers.preference.preference_list import (
    UserPreferenceListSerializer,
)
from apps.user.services.preference_list_service import get_user_preferences
from apps.user.services.preference_service import create_user_preferences
from typing import cast
from apps.user.models import User
from rest_framework import serializers, status


class PreferenceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["선호 장르"],
        summary="선호 장르 등록 API",
        request=UserPreferenceSerializer,
        responses={
            201: inline_serializer(
                name="PreferenceCreateResponse",
                fields={
                    "message": serializers.CharField(),
                },
            ),
        },
    )
    def post(self, request):
        # 1. 입력 데이터 검증
        serializer = UserPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 유저 타입 캐스팅 (Type Hinting)
        user = cast(User, request.user)

        # 3. 서비스 레이어 호출
        create_user_preferences(
            user=user,
            genre_ids=serializer.validated_data["genre_ids"],
        )

        return Response({"message": "저장 완료"}, status=201)

    @extend_schema(
        tags=["선호 장르"],
        summary="선호 장르 조회 API",
        responses=UserPreferenceListSerializer,
    )
    def get(self, request):
        # 1. 유저 타입 캐스팅 (Type Hinting)
        user = cast(User, request.user)

        # 2. 서비스 레이어 호출
        preferences = get_user_preferences(
            user=user,
        )

        # 3. 응답 데이터 검증
        serializer = UserPreferenceListSerializer(preferences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
