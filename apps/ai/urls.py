from django.urls import path

from apps.ai.views.review_summary_view import GameReviewSummaryAPIView
from apps.ai.views.user_tendency_view import UserTendencyAPIView

urlpatterns = [
    path("<int:game_id>", GameReviewSummaryAPIView.as_view(), name="game_summary"),
    path("user/tendency", UserTendencyAPIView.as_view(), name="user_tendency"),
]
