from django.db.models import Prefetch
from apps.community.models.reviews import Review
from apps.community.models.comments import ReviewComment


def get_review_detail_queryset(review_id: int) -> Review | None:
    """
    리뷰 상세 정보와 해당 리뷰의 댓글 목록을 함께 조회합니다.
    """
    return (
        Review.objects.filter(id=review_id, is_deleted=False)
        .select_related("user")  # 리뷰 작성자
        .prefetch_related(
            Prefetch(
                "comments",  # ReviewComment 역참조 이름
                queryset=ReviewComment.objects.filter(is_deleted=False)
                .select_related("user")  # 댓글 작성자
                .order_by("-created_at"),
            )
        )
        .first()  # 없으면 None 반환
    )
