from typing import Any

from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models.comments import ReviewComment
from apps.community.models.reviews import Review
from apps.user.models.user import User


def create_comment(
    *, author: User, review_id: int, validated_data: dict[str, Any]
) -> ReviewComment:
    """
    댓글 생성 비즈니스 로직
    """

    try:
        review = Review.objects.get(pk=review_id, is_deleted=False)
    except Review.DoesNotExist:
        raise ReviewNotFound()

    comment = ReviewComment.objects.create(
        user=author,
        review=review,
        content=validated_data["content"],
    )

    return comment