from django.db import models

from apps.core.models import TimeStampedModel
from apps.user.models.user import User


class UserSocialAccount(TimeStampedModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    provider_user_name = models.CharField(max_length=255)
    provider_email = models.CharField(max_length=255, null=True)
    connected_at = models.DateTimeField()
    created_at = models.DateTimeField()
