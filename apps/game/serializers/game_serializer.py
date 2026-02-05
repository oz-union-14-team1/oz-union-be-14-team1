from rest_framework import serializers
from apps.game.models import Game, Genre, Tag, Platform, GameImg


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
        fields = ["id", "name", "tags", "image", "released_at", "platforms",]

    def get_image(self, obj):
        first_image = obj.game_images.first()
        return first_image.img_url

    def get_tags(self, obj):
        tags = Tag.objects.filter(game_tags__game=obj)
        return [tag.tag for tag in tags]

    def get_platforms(self, obj):
        platforms = Platform.objects.filter(game_platforms__game=obj)
        return [platform.platform for platform in platforms]


class GameDetailSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    platforms = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

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
        ]

    def get_genres(self, obj):
        genres = Genre.objects.filter(game_genres__game=obj)
        return [genre.genre for genre in genres]

    def get_tags(self, obj):
        tags = Tag.objects.filter(game_tags__game=obj)
        return [tag.tag for tag in tags]

    def get_platforms(self, obj):
        platforms = Platform.objects.filter(game_platforms__game=obj)
        return [platform.platform for platform in platforms]

    def get_images(self, obj):
        images = obj.game_images.all()
        return [image.img_url for image in images]
