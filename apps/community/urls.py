from django.urls import path

from apps.community.views.review_api import GameReviewView

urlpatterns = [
    path("<int:game_id>/reviews", GameReviewView.as_view(), name="game_review_create"),
]
