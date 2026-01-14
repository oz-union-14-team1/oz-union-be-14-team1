from typing import Any

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel

from .validators import (
    validate_email_format,
    validate_phone_format,
    validate_nickname_format,
)


class UserManager(BaseUserManager["User"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        if not email:
            raise ValueError("이메일은 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class GenderChoices(models.TextChoices):
    MALE = "M", "MALE"
    FEMALE = "F", "FEMALE"


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.CharField(max_length=100,unique=True, validators=[validate_email_format])
    nickname = models.CharField(max_length=10, unique=True, validators=[validate_nickname_format])
    phone_number = models.CharField(max_length=20, validators=[validate_phone_format])
    gender = models.CharField(max_length=1,choices=GenderChoices.choices)
    profile_img_url = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    name = models.CharField(max_length=10, default="")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email
