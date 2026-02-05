from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.user.validators.validator import validate_user_password

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(read_only=True)

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
            "phone_number",
            "password",
        )
        read_only_fields = (
            "id",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "phone_number",
        )
        extra_kwargs = {
            "nickname": {"validators": []},
        }

    def validate_password(self, value):
        user = self.context["request"].user
        return validate_user_password(user, value)

    def validate_nickname(self, value: str) -> str:
        request = self.context.get("request")
        user = request.user if request else None

        value = (value or "").strip()

        if user and value == (user.nickname or ""):
            raise serializers.ValidationError("기존 닉네임과 동일합니다.")

        if user and User.objects.exclude(pk=user.pk).filter(nickname=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")

        return value

    def update(self, instance, validated_data):
        validated_data.pop("email", None)
        validated_data.pop("password", None)

        return super().update(instance, validated_data)


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        user = self.context["request"].user
        return validate_user_password(user, value)
