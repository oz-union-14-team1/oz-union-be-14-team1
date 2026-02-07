from typing import ClassVar, Any, cast

import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import IntegrityError
from apps.user.validators.validator import validate_user_password

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(read_only=True)

    new_password = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

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
            "new_password",
            "new_password_confirm",
        )
        read_only_fields = (
            "id",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "phone_number",
        )
        extra_kwargs: ClassVar[dict[str, Any]] = {
            "nickname": {"validators": []},
        }

    def validate(self, attrs):
        logger = logging.getLogger(__name__)

        logger.warning(
            "ME_UPDATE payload keys=%s new_pw=%r new_pw2=%r",
            list(attrs.keys()),
            attrs.get("new_password"),
            attrs.get("new_password_confirm"),
        )

        raw_new_pw = attrs.get("new_password", None)
        raw_new_pw2 = attrs.get("new_password_confirm", None)

        new_pw = (raw_new_pw or "").strip() if isinstance(raw_new_pw, str) else ""
        new_pw2 = (raw_new_pw2 or "").strip() if isinstance(raw_new_pw2, str) else ""

        if not new_pw and not new_pw2:
            attrs.pop("new_password", None)
            attrs.pop("new_password_confirm", None)
            return attrs

        if not new_pw or not new_pw2:
            raise serializers.ValidationError(
                {"new_password_confirm": "새 비밀번호 확인을 함께 입력해야 합니다."}
            )

        if new_pw != new_pw2:
            raise serializers.ValidationError(
                {"new_password_confirm": "새 비밀번호가 일치하지 않습니다."}
            )

        attrs["new_password"] = new_pw
        attrs["new_password_confirm"] = new_pw2
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("email", None)

        new_pw = validated_data.pop("new_password", None)
        validated_data.pop("new_password_confirm", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if new_pw:
            user = cast(AbstractBaseUser, instance)
            user.set_password(new_pw)

        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"nickname": "이미 사용 중인 닉네임입니다."}
            )

        return instance


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value: str) -> str:
        user = self.context["request"].user
        return validate_user_password(user, value)
