from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    intro = models.TextField()
    released_at = models.DateField(null=True, blank=True)
    developer = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    id_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "games"
