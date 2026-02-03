from django.urls import path
from apps.game.views.game_views import GameListView, GameDetailView, GameSearchView
from apps.game.views.wishlist_views import WishlistView, WishlistDestroyView
from apps.game.views.import_views import GameImportView
from apps.game.views.recommend_views import (
    GamePreferenceGameRecommendView,
    GamePreferenceTagRecommendView,
)


urlpatterns = [
    path("", GameListView.as_view(), name="game-list"),
    path("<int:pk>", GameDetailView.as_view(), name="game-detail"),
    path("wishlist", WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:pk>", WishlistDestroyView.as_view(), name="wishlist-destroy"),
    path("import", GameImportView.as_view(), name="game-import"),
    path("search", GameSearchView.as_view(), name="game-search"),
    path(
        "recommend/preference",
        GamePreferenceGameRecommendView.as_view(),
        name="game-recommend-preference",
    ),
    path(
        "api/v1/game/recommend/wishlist",
        GamePreferenceTagRecommendView.as_view(),
        name="game-recommend-wishlist",
    ),
]
