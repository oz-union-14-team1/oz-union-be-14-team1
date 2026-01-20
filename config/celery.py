import os
from celery import Celery  # type: ignore

# 1. Django 설정 파일 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# 2. settings.py에서 'CELERY_'로 시작하는 설정을 불러옴
app.config_from_object("django.conf:settings", namespace="CELERY")

# 3. 등록된 앱(apps)에서 자동으로 tasks.py를 찾음
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
