from django.db import models

from apps.core.models import TimeStampedModel
from apps.game.models.game import Game


class GameReviewSummary(TimeStampedModel):
    """
    요약된 리뷰 저장 테이블
    """

    game = models.OneToOneField(
        Game,
        on_delete=models.CASCADE,
        related_name="summary",
    )
    text = models.TextField(verbose_name="AI가 생성한 본문")

    class Meta:
        db_table = "game_review_summarise"
