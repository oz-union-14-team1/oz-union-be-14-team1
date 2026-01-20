from rest_framework import serializers
from apps.game.models.game import Game


class SummaryRequestSerializer(serializers.Serializer):
    """
    요청 검증용 Serializer
    """

    game_id = serializers.IntegerField()

    def validate_game_id(self, value):
        if not Game.objects.filter(id=value).exists():
            raise serializers.ValidationError("존재하지 않는 게임 ID입니다.")
        return value
