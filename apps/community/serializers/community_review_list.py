from rest_framework import serializers
from apps.community.models.reviews import Review
from apps.community.serializers.review.review_list import ReviewListSerializer

class CommunityReviewListSerializer(ReviewListSerializer):
    """
    기존 리뷰 리스트 정보 + 게임 정보 추가
    """
    game_title = serializers.CharField(source="game.name", read_only=True)

    class Meta(ReviewListSerializer.Meta):
        model = Review
        fields = ReviewListSerializer.Meta.fields + ["game_title"]