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


class GamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 40


class GameListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        games = Game.objects.filter(id_deleted=False).order_by("-release_date")

        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(
            games, request
        )  # 전체데이터(games) / 페이지(request)

        serializer = GameListSerializer(paginated_games, many=True)

        return paginator.get_paginated_response(serializer.data)


class GameDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk, id_deleted=False)
        serializer = GameDetailSerializer(game)

        return Response(serializer.data)


class GameSearchByTagView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tag_slug = request.query_params.get("tag")

        if not tag_slug:
            return Response({"error": "tag 파라미터가 필요합니다."}, status=400)

        try:
            tag = Tag.objects.get(slug=tag_slug)
        except Tag.DoesNotExist:
            return Response(
                {"error": f"'{tag_slug}' 태그를 찾을 수 없습니다."}, status=404
            )

        games = (
            Game.objects.filter(game_tags__tag=tag, id_deleted=False)
            .order_by("-released_at")
            .distinct()
        )

        # 페이지네이션
        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(games, request)

        # Serializer로 변환
        serializer = GameListSerializer(paginated_games, many=True)

        # 응답
        return paginator.get_paginated_response(serializer.data)
