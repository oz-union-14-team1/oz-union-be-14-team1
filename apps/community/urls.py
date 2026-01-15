from django.urls import path

from apps.community.views.review_api import ReviewAPIView
from apps.community.views.review_like_api import ReviewLikeAPIView

urlpatterns = [
    path("<int:game_id>/reviews", ReviewAPIView.as_view(), name="game_review_create"),
    path(
        "reviews/<int:review_id>/like", ReviewLikeAPIView.as_view(), name="review_like"
    ),
]
