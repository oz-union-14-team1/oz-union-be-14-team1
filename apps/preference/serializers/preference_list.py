from rest_framework import serializers


class TagInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(source="name")  # type: ignore


class GenreInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(source="Genre")  # type: ignore


class UserPreferenceResponseSerializer(serializers.Serializer):
    Tags = TagInfoSerializer(many=True)
    Genres = GenreInfoSerializer(many=True)
