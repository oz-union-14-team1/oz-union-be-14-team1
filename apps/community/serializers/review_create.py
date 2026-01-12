from rest_framework import serializers

from apps.community.models.reviews import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["content", "rating"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("별점은 1에서 5 사이의 정수여야 합니다.")
        return value
