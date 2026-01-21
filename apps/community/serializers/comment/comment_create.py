from rest_framework import serializers

from apps.community.models.comments import ReviewComment


class ReviewCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ["content"]