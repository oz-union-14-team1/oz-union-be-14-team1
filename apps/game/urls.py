from django.urls import path
from apps.game.views.game_views import GameListView, GameDetailView
from apps.game.views.wishlist_views import WishlistView, WishlistDetailView


urlpatterns = [
    path('', GameListView.as_view(), name='game-list'),
    path('<int:pk>/', GameDetailView.as_view(), name='game-detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', WishlistDetailView.as_view(), name='wishlist-detail'),

]