from django.db import models

from apps.user.models.user import User
from apps.game.models.genre import Genre


class Preference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, db_column="genre_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "preference"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "genre"],
                name="unique_user_preference",
            )
        ]
