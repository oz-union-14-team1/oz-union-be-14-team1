from celery import shared_task
from apps.ai.services import ReviewSummaryService
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_ai_summary(game_id):
    """
    Celery가 실행할 백그라운드 작업
    """
    logger.info(f"Start AI Summary Task for Game ID: {game_id}")

    try:
        service = ReviewSummaryService()
        service.get_summary(game_id)
        logger.info(f"Successfully finished summary for Game ID: {game_id}")

    except Exception as e:
        logger.error(f"Error in AI Summary Task: {e}")