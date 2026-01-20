from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai"

    def ready(self):
        # Django 시작 시 signals 모듈을 임포트하여 작동하게 함
        pass
