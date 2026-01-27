from django.db import models


class TagCategory(models.Model):
    """
    태그 대분류를 관리하는 모델
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    class Meta:
        db_table = "tag_category"
        verbose_name = "태그 대분류"

    def __str__(self):
        return self.name
