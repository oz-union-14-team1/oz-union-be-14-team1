from django.db import models
from apps.game.models.game import Game


class GameImg(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_images")
    img_url = models.TextField()

    class Meta:
        db_table = "game_img"
