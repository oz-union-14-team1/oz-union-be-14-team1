from rest_framework.views import APIView

from apps.game.models.game_tag import GameTag
from apps.game.models.game import Game
from apps.game.models.wishlist import Wishlist
from apps.game.serializers.game_serializer import GameListSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.preference.models import TagPreference
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count


class GamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 40


class GamePreferenceGameRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["게임"],
        summary="선호 태그 기반 게임 추천 api",
        responses=GameListSerializer,
    )
    def get(self, request):
        pref_tag_ids = TagPreference.objects.filter(user=request.user).values_list(
            "tag_id", flat=True
        )

        games = (
            Game.objects.filter(
                game_tags__tag_id__in=pref_tag_ids,
                is_deleted=False,
            )
            .prefetch_related("game_images")
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


class GamePreferenceTagRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["게임"],
        summary="위시리스트 기반 게임 추천 api",
        responses=GameListSerializer,
    )
    def get(self, request):
        wishlist_game_ids = Wishlist.objects.filter(user=request.user).values_list(
            "game_id", flat=True
        )

        wishlist_tags = (
            GameTag.objects.filter(game_id__in=wishlist_game_ids)
            .values("tag_id")
            .annotate(tag_count=Count("tag_id"))
            .order_by("-tag_count")
        )

        pref_tag_ids = [tag["tag_id"] for tag in wishlist_tags]

        games = (
            Game.objects.filter(
                game_tags__tag_id__in=pref_tag_ids,
                is_deleted=False,
            )
            .exclude(id__in=wishlist_game_ids)
            .prefetch_related("game_images")
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
