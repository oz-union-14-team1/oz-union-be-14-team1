from django.db import models


class Platform(models.Model):
    platform = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        db_table = "platform"
