from rest_framework import serializers

from apps.user.models.user import User


class AuthorSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_img_url",
        ]
