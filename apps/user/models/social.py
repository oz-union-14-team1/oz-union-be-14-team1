from django.db import models
from django.conf import settings

class SocialAccount(models.Model):
    provider = models.CharField(max_length=20, default='google') # 'google', 'discord'
    social_id = models.CharField(max_length=255) # 구글의 고유 ID
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_accounts"
        # 한 provider 내에서 social_id는 유일해야 함
        unique_together = ('provider', 'social_id')

    def __str__(self):
        return f"{self.provider} - {self.user.email}"