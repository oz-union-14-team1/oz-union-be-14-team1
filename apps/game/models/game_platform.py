from django.db import models
from apps.game.models.game import Game


class GamePlatform(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    platform_name = models.CharField(max_length=255)
    platform_url = models.TextField()

    class Meta:
        db_table = "game_platform"
