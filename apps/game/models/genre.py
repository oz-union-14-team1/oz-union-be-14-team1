from django.db import models


class Genre(models.Model):
    Genre = models.CharField(max_length=255)
    Genre_ko = models.CharField(max_length=255)

    class Meta:
        db_table = "genre"
