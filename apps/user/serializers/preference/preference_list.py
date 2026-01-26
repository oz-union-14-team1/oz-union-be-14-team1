from rest_framework import serializers
from apps.user.models.preference import Preference


class UserPreferenceListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="genre.id")
    name = serializers.CharField(source="genre.Genre")
    name_ko = serializers.CharField(source="genre.Genre_ko")

    class Meta:
        model = Preference
        fields = ["id", "name", "name_ko"]
