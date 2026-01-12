from django.db import models

from apps.game.models.game import Game
from apps.user.models.user import User


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = "wishlist"
