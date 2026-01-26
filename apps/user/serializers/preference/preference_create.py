from rest_framework import serializers
from apps.game.models.genre import Genre


class UserPreferenceSerializer(serializers.Serializer):
    genre_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    def validate_genre_ids(self, value):
        # 1. 빈 리스트 체크
        if not value:
            raise serializers.ValidationError("최소 하나의 장르를 선택해야 합니다.")

        # 2. 중복 제거(ex. [1, 1])
        unique_input_ids = set(value)

        # 3. DB에 존재하는 ID인지 조회
        valid_ids = set(
            Genre.objects.filter(id__in=unique_input_ids).values_list("id", flat=True)
        )
        if len(unique_input_ids) != len(valid_ids):
            raise serializers.ValidationError("존재하지 않는 장르가 포함되어 있습니다.")

        return list(unique_input_ids)
