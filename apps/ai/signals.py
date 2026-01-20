from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from apps.community.models.reviews import Review
from apps.ai.tasks import run_ai_summary


@receiver(post_save, sender=Review)
def trigger_ai_summary(sender, instance, created, **kwargs):
    """
    리뷰가 저장(post_save)될 때마다 실행되는 함수
    """
    # 1. 수정된 리뷰는 무시하고, 새로 생성된 리뷰일 때만 체크
    if not created:
        return

    game = instance.game

    # 설정값 로드
    MIN_COUNT = getattr(settings, 'AI_SUMMARY_MIN_REVIEW_COUNT', 10)
    UPDATE_DAYS = getattr(settings, 'AI_SUMMARY_UPDATE_INTERVAL_DAYS', 30)

    # 2. 현재 유효 리뷰 개수 확인
    current_count = game.reviews.filter(is_deleted=False).count()

    # 조건1: 리뷰 개수가 기준(10개) 이상인가?
    if current_count >= MIN_COUNT:
        summary_obj = getattr(game, 'summary', None)

        should_run = False

        # 조건1-1: 요약본이 아예 없으면 -> 실행
        if not summary_obj:
            should_run = True

        # 조건1-2: 요약본이 있지만, 마지막 업데이트로부터 30일 지났으면 -> 실행
        else:
            time_diff = timezone.now() - summary_obj.updated_at
            if time_diff > timedelta(days=UPDATE_DAYS):
                should_run = True

        # 실행 조건 만족 시 Celery Task 호출
        if should_run:
            print(f"[Signal] Triggering AI Summary for Game {game.id}")
            run_ai_summary.delay(game.id)