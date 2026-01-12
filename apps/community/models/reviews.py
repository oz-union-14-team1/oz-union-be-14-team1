from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.core.models import TimeStampedModel
from apps.game.models.game import Game
from apps.user.models.user import User


class Review(TimeStampedModel):
    """
    리뷰 저장 테이블
    """

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    content = models.TextField(verbose_name="리뷰 내용")
    rating = models.PositiveSmallIntegerField(
        verbose_name="별점",
        validators=[MinValueValidator(1), MaxValueValidator(5)],  # 1~5점 제한
        help_text="1~5 사이의 정수",
    )
    view_count = models.BigIntegerField(default=0, verbose_name="조회수")
    like_count = models.BigIntegerField(default=0, verbose_name="좋아요 합계")

    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "reviews"
        indexes = [
            models.Index(fields=["game", "-like_count"], name="idx_reviews_best"),
        ]
