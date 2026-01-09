from django.db import models
from apps.game.models import Game

class GameReviewSummary(models.Model):
    """
    요약된 리뷰 저장 테이블
    """
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='summaries',
    )
    text = models.TextField(verbose_name="AI가 생성한 본문")

    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성된 시간")

    class Meta:
        db_table = 'game_review_summarise'