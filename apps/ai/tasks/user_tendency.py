from celery import shared_task  # type: ignore
from django.contrib.auth import get_user_model
import logging


logger = logging.getLogger(__name__)


@shared_task
def run_user_tendency_analysis(user_id: int):
    """
    유저 ID를 받아 성향 분석을 비동기로 수행
    """
    from apps.ai.services.user_tendency_service import UserTendencyService
    from django.core.cache import cache

    User = get_user_model()

    cache_key = f"tendency_analysis_lock_{user_id}"
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Start User Tendency Analysis for User ID: {user_id}")

        # 서비스의 분석 로직 호출
        service = UserTendencyService()
        service.analyze_and_save(user)
        logger.info(f"Successfully finished analysis for User ID: {user_id}")

    except User.DoesNotExist:
        logger.error(f"User not found during tendency analysis: {user_id}")
    except Exception as e:
        logger.error(f"Error in User Tendency Task: {e}", exc_info=True)
    finally:
        # 성공하든 실패하든 작업끝나면 무조건 락 해제
        cache.delete(cache_key)
