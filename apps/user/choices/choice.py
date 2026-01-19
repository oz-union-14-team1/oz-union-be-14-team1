from django.db import models


class Gender(models.TextChoices):
    MALE = "M", "MALE"
    FEMALE = "F", "FEMALE"
