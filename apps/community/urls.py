from django.urls import path

from apps.community.views.review_api import ReviewAPIView

urlpatterns = [
    path("<int:game_id>/reviews", ReviewAPIView.as_view(), name="game_review_create"),
]
