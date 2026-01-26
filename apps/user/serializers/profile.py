from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nickname",
            "name",
            "gender",
            "is_active",
            "created_at",
            "updated_at",
            "password",
        )
        read_only_fields = (
            "id",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        )

    def update(self, instance, validated_data):
        validated_data.pop("email", None)
        validated_data.pop("password", None)

        return super().update(instance, validated_data)


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("비밀번호가 올바르지 않습니다.")
        return value
