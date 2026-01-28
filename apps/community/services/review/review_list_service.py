from django.db.models import QuerySet
from apps.community.models.reviews import Review


def get_review_list(game_id: int) -> QuerySet[Review]:
    """
    특정 게임의 리뷰 목록을 최신순으로 조회합니다.
    user 정보를 함께 가져오기 위해 select_related를 사용합니다 (N+1 방지)
    """
    return (
        Review.objects.filter(game_id=game_id, is_deleted=False)  # type: ignore
        .select_related("user", "game")  # Review 모델의 user 필드를 미리 조인해서 가져옴
        .order_by("-created_at")  # 최신순 정렬
    )
