from django.db import models
from django.db.models import UniqueConstraint

from apps.game.models.game import Game
from apps.game.models.publisher import Publisher


class GamePublisher(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    class Meta:
        db_table = "game_publisher"
        UniqueConstraint(fields=["game", "publisher"], name="unique_publisher")
