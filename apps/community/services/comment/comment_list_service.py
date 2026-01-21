from django.db.models import QuerySet

from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models import Review
from apps.community.selectors.review_comment_selector import get_review_detail_queryset


def get_review_comment_detail(*, review_id: int) -> QuerySet[Review]:
    """
    특정 게임의 리뷰 목록과 리뷰에 작성된 댓글들을 가져옵니다.
    """
    # 1. Selector 호출
    review = get_review_detail_queryset(review_id)

    # 2. 결과 검증
    if not review:
        raise ReviewNotFound()

    return review  # type: ignore
