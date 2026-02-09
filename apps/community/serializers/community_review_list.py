from rest_framework import serializers
from apps.community.models.reviews import Review
from apps.community.serializers.review.review_list import ReviewListSerializer


class CommunityReviewListSerializer(ReviewListSerializer):
    """
    기존 리뷰 리스트 정보 + 게임 정보 + 장르 정보
    """
    game_id = serializers.IntegerField(source="game.id", read_only=True)
    game_title = serializers.CharField(source="game.name", read_only=True)
    game_genres = serializers.SerializerMethodField()

    class Meta(ReviewListSerializer.Meta):
        model = Review
        fields = ReviewListSerializer.Meta.fields + ["game_id", "game_title", "game_genres"]

    def get_game_genres(self, obj):
        """
        해당 리뷰가 달린 게임의 모든 장르 명칭을 리스트로 반환
        ex. ["RPG", "Action"]
        """
        return [gg.genre.genre for gg in obj.game.game_genres.all()]
        """
        obj.game -> Game 객체
        obj.game.game_genres -> GameGenre 역참조 매니저
        gg.genre.genre -> Genre 모델의 genre 필드 (이름)
        """
