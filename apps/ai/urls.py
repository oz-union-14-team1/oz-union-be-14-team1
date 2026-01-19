from django.urls import path

from apps.ai.views import GameReviewSummaryAPIView

urlpatterns = [
    path("<int:game_id>", GameReviewSummaryAPIView.as_view(), name="game_summary"),
]
