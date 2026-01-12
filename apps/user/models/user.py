from django.db import models

from apps.core.models import TimeStampedModel


class User(TimeStampedModel):
    email = models.EmailField()
    hashed_password = models.CharField(max_length=255)
    nickname = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    profile_img_url = models.TextField(blank=True, null=True)
