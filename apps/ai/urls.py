from django.urls import path

from apps.ai.views.review_summary_view import GameReviewSummaryAPIView

urlpatterns = [
    path("<int:game_id>", GameReviewSummaryAPIView.as_view(), name="game_summary"),
]
