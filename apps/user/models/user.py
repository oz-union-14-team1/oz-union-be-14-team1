from typing import Any

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel
from apps.user.utils.nickname import generate_nickname


class UserManager(BaseUserManager["User"]):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        if not email:
            raise ValueError("이메일은 필수입니다.")

        email = self.normalize_email(email)

        # nickname 자동 생성
        if not extra_fields.get("nickname"):
            nickname = generate_nickname()
            for _ in range(5):
                if not User.objects.filter(nickname=nickname).exists():
                    break
                nickname = generate_nickname()
            else:
                raise ValueError("닉네임 자동 생성 실패")

            extra_fields["nickname"] = nickname

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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("슈퍼유저는 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("슈퍼유저는 is_superuser=True 여야 합니다.")

        return self.create_user(email, password, **extra_fields)


class GenderChoices(models.TextChoices):
    MALE = "M", "MALE"
    FEMALE = "F", "FEMALE"


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=15, unique=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GenderChoices.choices, blank=True, null=True
    )

    profile_img_url = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email
