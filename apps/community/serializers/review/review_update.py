from rest_framework import serializers

from apps.community.models.reviews import Review


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "content",
            "rating",
        ]
