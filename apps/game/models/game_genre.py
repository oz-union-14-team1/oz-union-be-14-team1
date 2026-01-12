from django.db import models
from apps.game.models.game import Game
from apps.game.models.genre import Genre


class GameGenre(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = "game_genre"
