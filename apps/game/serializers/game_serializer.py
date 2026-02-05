from rest_framework import serializers
from apps.game.models import Game, Genre, Tag, Platform, GameImg
from apps.community.models.reviews import Review
from django.db.models import Avg

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            "id",
            "genre",
            "slug",
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "tag",
            "slug",
        ]


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["id", "platform", "slug"]


class GameImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameImg
        fields = ["id", "img_url"]


class GameListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    platforms = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "tags",
            "image",
            "released_at",
            "platforms",
        ]

    def get_image(self, obj):
        first_image = obj.game_images.first()
        return first_image.img_url

    def get_tags(self, obj):
        return [game_tag.tag.tag for game_tag in obj.game_tags.all()]

    def get_platforms(self, obj):
        return [game_platform.platform.platform for game_platform in obj.game_platforms.all()]


class GameDetailSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    platforms = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    avg_score = serializers.SerializerMethodField()
    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "intro",
            "developer",
            "publisher",
            "released_at",
            "genres",
            "tags",
            "platforms",
            "images",
            "avg_score"
        ]

    def get_genres(self, obj):
        return [game_genre.genre.genre for game_genre in obj.game_genres.all()]

    def get_tags(self, obj):
        return [game_tag.tag.tag for game_tag in obj.game_tags.all()]

    def get_platforms(self, obj):
        return [game_platform.platform.platform for game_platform in obj.game_platforms.all()]

    def get_images(self, obj):
        return [image.img_url for image in obj.game_images.all()]

    def get_avg_score(self, obj):
        return round(obj.avg_score, 1) if obj.avg_score else 0
