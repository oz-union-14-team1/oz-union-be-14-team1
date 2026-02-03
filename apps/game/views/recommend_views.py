from rest_framework.views import APIView
from apps.game.models import Game
from apps.game.serializers.game_serializer import (
    GameListSerializer
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.preference.models import TagPreference
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count

class GamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 40

class GameRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["게임"],
        summary="선호 태그 기반 게임 추천 api",
        responses=GameListSerializer,
    )
    def get(self, request):
        user_tag_preferences = TagPreference.objects.filter(
            user=request.user
        ).select_related("tag")

        pref_tag_ids = [pref.tag_id for pref in user_tag_preferences]

        games = (
            Game.objects.filter(
                game_tags__tag_id__in=pref_tag_ids,
                is_deleted=False,
            )
            .annotate(
                matching_tags_count=Count(
                    "game_tags",
                    filter=Q(game_tags__tag_id__in=pref_tag_ids),
                    distinct=True,
                )
            )
            .order_by("-matching_tags_count", "-released_at")
            .distinct()
        )

        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(games, request)

        serializer = GameListSerializer(paginated_games, many=True)

        return paginator.get_paginated_response(serializer.data)