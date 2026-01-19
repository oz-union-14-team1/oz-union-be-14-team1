from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel
from apps.user.validators.validator import (
    validate_email_format,
    validate_phone_format,
    validate_nickname_format,
)
from apps.user.choices import Gender
from apps.user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.CharField(
        max_length=100, unique=True, validators=[validate_email_format]
    )
    name = models.CharField(max_length=10, default="")
    nickname = models.CharField(
        max_length=10, unique=True, validators=[validate_nickname_format]
    )
    phone_number = models.CharField(max_length=20, validators=[validate_phone_format])
    gender = models.CharField(max_length=1, choices=Gender.choices)
    profile_img_url = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return f"{self.nickname} {(self.email)}"
