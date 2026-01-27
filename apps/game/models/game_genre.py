from django.db import models
from apps.game.models.game import Game
from apps.game.models.genre import Genre


class GameGenre(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_genres")
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, related_name="game_genres"
    )

    class Meta:
        db_table = "game_genres"
        unique_together = [["game", "genre"]]
