from django.db.models import QuerySet
from apps.community.models.reviews import Review

def get_community_review_all() -> QuerySet[Review]:
    """
    커뮤니티용 전체 리뷰 피드를 조회합니다.
    모든 게임의 리뷰를 최신순으로 가져오며, 게임 정보도 함께 로딩합니다.
    """
    return (
        Review.objects.filter(is_deleted=False)
        .select_related("user", "game")
        .order_by("-created_at")
    )