from django.urls import path
from apps.game.views.game_views import GameListView, GameDetailView

urlpatterns = [
    path('', GameListView.as_view(), name='game-list'),
    path('<int:pk>/', GameDetailView.as_view(), name='game-detail'),
]