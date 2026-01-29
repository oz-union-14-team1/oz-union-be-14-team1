from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.game.models import Tag
from apps.game.models import Genre
from apps.game.serializers.game_serializer import GenreSerializer, TagSerializer
from apps.preference.serializers.preference_create import UserPreferenceSerializer
from apps.preference.serializers.preference_list import UserPreferenceResponseSerializer
from apps.preference.services.preference_list_service import get_user_total_preferences
from apps.preference.services.preference_service import update_user_total_preferences


class PreferenceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["선호도"],
        summary="사용자 선호도(태그/장르) 조회",
        responses=UserPreferenceResponseSerializer,
    )
    def get(self, request):
        # 1. 서비스 호출
        data = get_user_total_preferences(request.user)

        # 2. 응답 직렬화
        response_serializer = UserPreferenceResponseSerializer(instance=data)

        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["선호도"],
        summary="사용자 선호도(태그/장르) 저장/수정",
        request=UserPreferenceSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            }
        },
    )
    def post(self, request):
        # 1. 입력 검증
        serializer = UserPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 서비스 호출 (저장/수정 통합)
        update_user_total_preferences(
            user=request.user,
            tag_ids=serializer.validated_data.get("Tags", []),
            genre_ids=serializer.validated_data.get("Genres", []),
        )

        return Response(
            {"success": True, "message": "저장 완료"}, status=status.HTTP_200_OK
        )


class GenreListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["선호도"],
        summary="전체 장르 목록 조회",
    )
    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagListAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["선호도"],
        summary="전체 태그 목록 조회",
    )
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
