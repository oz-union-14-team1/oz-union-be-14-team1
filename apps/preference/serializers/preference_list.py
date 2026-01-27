from rest_framework import serializers


class TagInfoSerializer(serializers.Serializer):
    """
    태그 정보 조회 시 반환할 필드 정의
    """

    id = serializers.IntegerField()
    tag = serializers.CharField()  # type: ignore


class GenreInfoSerializer(serializers.Serializer):
    """
    장르 정보 조회 시 반환할 필드 정의
    """

    id = serializers.IntegerField()
    genre = serializers.CharField()  # type: ignore


class UserPreferenceResponseSerializer(serializers.Serializer):
    """
    최종 응답 구조: Tags 리스트와 Genres 리스트 포함
    """

    Tags = TagInfoSerializer(many=True)
    Genres = GenreInfoSerializer(many=True)
