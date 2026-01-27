from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.ai.tasks.user_tendency import run_user_tendency_analysis
from apps.preference.models import GenrePreference, TagPreference


@receiver(post_save, sender=GenrePreference)
@receiver(post_save, sender=TagPreference)
def trigger_user_tendency_analysis(sender, instance, created, **kwargs):
    """
    유저 선호도가 저장(수정/생성)되면 성향 분석 Task 실행
    """
    # AI 기능 비활성화 옵션 확인
    if getattr(settings, "DISABLE_AI_ANALYSIS", False):
        return

    # instance.user를 통해 유저 객체에 접근 가능하다고 가정
    user = getattr(instance, 'user', None)

    if user:
        # 비동기 작업 예약
        print(f"[Signal] Triggering AI Tendency Analysis for User {user.id}")
        run_user_tendency_analysis.delay(user.id)