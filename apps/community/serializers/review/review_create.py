from rest_framework import serializers

from apps.community.models.reviews import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["content", "rating"]
        extra_kwargs = {
            "rating": {
                "error_messages": {
                    "min_value": "별점은 1에서 5 사이의 정수여야 합니다.",
                    "max_value": "별점은 1에서 5 사이의 정수여야 합니다.",
                }
            },
            "content": {
                "max_length": 300,
            },
        }
