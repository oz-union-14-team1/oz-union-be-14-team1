from rest_framework import serializers

from apps.community.models import ReviewComment, Review
from apps.community.serializers.common.author_serializer import AuthorSerializer


class CommentListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user", read_only=True)

    class Meta:
        model = ReviewComment
        fields = [
            "id",
            "author",
            "content",
            "created_at",
        ]


class ReviewCommentListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(source="user", read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)
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
            "comments",
        ]
