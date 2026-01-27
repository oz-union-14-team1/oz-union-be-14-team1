from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        db_table = "tag"