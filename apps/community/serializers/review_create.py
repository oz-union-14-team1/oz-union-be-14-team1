from rest_framework import serializers

from apps.community.models.reviews import Review

class ReviewSerializer(serializers.ModelSerializer[Review]):
    class Meta:
        model = Review
        fields= [
            'content',
            'rating',
        ]