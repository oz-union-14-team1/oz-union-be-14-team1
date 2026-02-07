from django.db import models
from django.conf import settings

from apps.core.models import TimeStampedModel


class UserTendency(TimeStampedModel):
    """
    유저의 AI 분석 성향을 저장하는 모델
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_tendency",
    )
    tendency = models.CharField(
        max_length=20,
        help_text="AI가 분석한 10자 이내의 게이머 성향",
        null = True,
        blank = True
    )

    class Meta:
        db_table = "user_tendency"

    def __str__(self):
        return f"{self.user} - {self.tendency}"
