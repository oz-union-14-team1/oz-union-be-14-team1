from django.db import models

from apps.user.models.user import User


class UserSocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    provider = models.CharField(max_length=20)
    provider_user_name = models.CharField(max_length=255)
    provider_email = models.CharField(max_length=255, null=True)
    connected_at = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "social_account"