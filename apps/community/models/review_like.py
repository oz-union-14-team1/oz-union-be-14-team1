from django.conf import settings
from django.db import models

from apps.community.models.reviews import Review


class ReviewLike(models.Model):
    """
    댓글(리뷰) 투표/좋아요 테이블
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_reviews",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성된 날짜")

    class Meta:
        db_table = "review_like"
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"], name="uk_review_like_user"
            )
        ]
