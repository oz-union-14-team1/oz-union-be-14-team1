from django.db import models
from apps.user.models.user import User
from apps.preference.models.tag import Tag

class TagPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id", related_name="user_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column="tag_id", related_name="preferred_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_tag_preference"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tag"],
                name="unique_user_tag_preference",
            )
        ]