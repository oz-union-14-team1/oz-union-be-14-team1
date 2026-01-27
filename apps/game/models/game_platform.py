from django.db import models
from apps.game.models.game import Game
from apps.game.models.platform import Platform


class GamePlatform(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="game_platforms"
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="game_platforms"
    )

    class Meta:
        db_table = "game_platforms"
        unique_together = [["game", "platform"]]
