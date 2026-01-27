from rest_framework import serializers

class TagInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(source="name")

class GenreInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(source="Genre")

class UserPreferenceResponseSerializer(serializers.Serializer):
    Tags = TagInfoSerializer(many=True)
    Genres = GenreInfoSerializer(many=True)
