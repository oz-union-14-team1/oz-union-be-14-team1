from django.db import models

from apps.preference.models.tag_category import TagCategory


class Tag(models.Model):
    """
    태그 정보를 관리하는 모델
    """
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(
        TagCategory, 
        on_delete=models.CASCADE, 
        db_column='category_id',
        related_name='tags'
    )
    name = models.CharField(max_length=255)
    label = models.TextField()

    class Meta:
        db_table = 'tag'
        verbose_name = '태그'
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_category_tag",
            )
        ]

    def __str__(self):
        return self.name