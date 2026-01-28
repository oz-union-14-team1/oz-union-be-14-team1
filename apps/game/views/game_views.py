from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from apps.game.models import Game
from apps.game.serializers.game_serializer import GameListSerializer,GameDetailSerializer


class GamePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 40


class GameListView(APIView):

    def get(self, request):
        games = Game.objects.filter(id_deleted=False).order_by("-release_date")

        paginator = GamePagination()
        paginated_games = paginator.paginate_queryset(games, request) # 전체데이터(games) / 페이지(request)

        serializer = GameListSerializer(paginated_games, many=True)

        return paginator.get_paginated_response(serializer.data)


class GameDetailView(APIView):

    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk, id_deleted=False)
        serializer = GameDetailSerializer(game)

        return Response(serializer.data)
