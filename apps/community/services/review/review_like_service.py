from django.db import transaction
from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models.reviews import Review
from apps.community.models.review_like import ReviewLike
from apps.user.models.user import User


def _get_review_with_lock(review_id: int) -> Review:
    """
    리뷰를 Lock과 함께 조회하고, 없으면 예외를 발생시킴
    """
    try:
        return Review.objects.select_for_update().get(id=review_id, is_deleted=False)  # type: ignore
    except Review.DoesNotExist:
        raise ReviewNotFound()


@transaction.atomic
def add_review_like(user: User, review_id: int) -> int:
    """
    좋아요 생성 (POST)
    """
    # 1. 공통 함수 호출 (Lock)
    review = _get_review_with_lock(review_id)

    # 2. 좋아요 생성 (get_or_create)
    like_obj, created = ReviewLike.objects.get_or_create(user=user, review=review)  # type: ignore

    if created:
        review.like_count += 1
        review.save(update_fields=["like_count"])

    return review.like_count


@transaction.atomic
def remove_review_like(user: User, review_id: int) -> int:
    """
    좋아요 삭제 (DELETE)
    """
    # 1. 공통 함수 호출 (Lock)
    review = _get_review_with_lock(review_id)

    # 2. 좋아요 삭제
    deleted_count, _ = ReviewLike.objects.filter(user=user, review=review).delete()  # type: ignore

    if deleted_count > 0:
        review.like_count -= 1
        review.save(update_fields=["like_count"])

    return review.like_count
