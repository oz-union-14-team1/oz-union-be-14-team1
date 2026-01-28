from rest_framework import serializers

from apps.community.models.reviews import Review
from apps.community.serializers.common.author_serializer import AuthorSerializer


class ReviewListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user", read_only=True)
    game_name = serializers.CharField(source="game.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "game_name",
            "author",
            "content",
            "rating",
            "like_count",
            "created_at",
        ]
