from django.db import models
from apps.core.models import TimeStampedModel
from apps.community.models.reviews import Review
from apps.user.models.user import User


class Comment(TimeStampedModel):
    """
    리뷰 댓글 저장 테이블
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="written_comments",
    )
    content = models.TextField(verbose_name="댓글내용")

    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "comments"
