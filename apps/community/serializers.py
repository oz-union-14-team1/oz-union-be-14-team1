from rest_framework import serializers
from .models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "nickname", "content", "rating", "created_at", "updated_at"]
        read_only_fields = ["id", "nickname", "created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Comment

        fields = ["id", "comment_id", "nickname", "content", "created_at", "updated_at"]

    def to_representation(self, instance):
        #  "comment_id" 키
        rep = super().to_representation(instance)
        rep["comment_id"] = rep.pop("id")
        return rep
