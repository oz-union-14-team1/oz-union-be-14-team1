from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from apps.game.models import Game, Tag
from apps.game.serializers.game_serializer import (
    GameListSerializer,
    GameDetailSerializer,
)
from rest_framework.permissions import AllowAny
from django.db.models import Q
from drf_spectacular.utils import extend_schema


class GamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 40

@extend_schema(tags=["게임"])
class GameListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="게임 전체 목록 제공 api",
        responses=GameListSerializer,
    )
    def get(self, request):
        games = Game.objects.filter(id_deleted=False).order_by("-release_at")

        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(
            games, request
        )  # 전체데이터(games) / 페이지(request)

        serializer = GameListSerializer(paginated_games, many=True)

        return paginator.get_paginated_response(serializer.data)

@extend_schema(tags=["게임"])
class GameDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="게임 상세 정보 제공 api",
        responses=GameDetailSerializer,
    )
    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk, id_deleted=False)
        serializer = GameDetailSerializer(game)

        return Response(serializer.data)

@extend_schema(tags=["게임"])
class GameSearchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="게임 상세 검색 제공 api",
        responses=GameListSerializer,
    )
    def get(self, request):
        query = request.query_params.get("q")

        if not query:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tag = Tag.objects.filter(Q(slug=query) | Q(tag_ko=query)).first()

        if tag:
            games = (
                Game.objects.filter(game_tags__tag=tag, is_deleted=False)
                .order_by("-released_at")
                .distinct()
            )
        else:
            games = Game.objects.filter(
                name__icontains=query, is_deleted=False
            ).order_by("-released_at")

        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(games, request)

        serializer = GameListSerializer(paginated_games, many=True)

        return paginator.get_paginated_response(serializer.data)
