from rest_framework import serializers
from apps.game.models.genre import Genre
from apps.preference.models.tag import Tag

class UserPreferenceSerializer(serializers.Serializer):
    Tags = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    Genres = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def _validate_ids(self, value, model, error_msg):
        """
        DB 존재 여부를 확인하는 공통 검증 함수
        """
        if not value:
            return []

        unique_ids = set(value)
        valid_ids = set(model.objects.filter(id__in=unique_ids).values_list("id", flat=True))

        if len(unique_ids) != len(valid_ids):
            raise serializers.ValidationError(error_msg)

        return list(unique_ids)

    def validate_Tags(self, value):
        return self._validate_ids(
            value,
            Tag,
            "존재하지 않는 태그가 포함되어 있습니다."
        )

    def validate_Genres(self, value):
        return self._validate_ids(
            value,
            Genre,
            "존재하지 않는 장르가 포함되어 있습니다."
        )