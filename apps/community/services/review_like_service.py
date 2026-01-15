from django.db import transaction
from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models.reviews import Review
from apps.community.models.review_like import ReviewLike
from apps.user.models.user import User


@transaction.atomic
def add_review_like(user: User, review_id: int) -> int:
    """
    좋아요 생성 (POST)
    """
    try:
        # 1. 리뷰 가져오기 (Lock)
        review = Review.objects.select_for_update().get(id=review_id)  # type: ignore
    except Review.DoesNotExist:
        raise ReviewNotFound()

    # 2. 좋아요 생성 (get_or_create)
    like_obj, created = ReviewLike.objects.get_or_create(user=user, review=review)  # type: ignore

    if created:
        review.like_count += 1
        review.save(update_fields=["like_count"])  # 필요한 컬럼만 수정

    return review.like_count


@transaction.atomic
def remove_review_like(user: User, review_id: int) -> int:
    """
    좋아요 삭제 (DELETE)
    """
    try:
        # 1. 리뷰 가져오기 (Lock)
        review = Review.objects.select_for_update().get(id=review_id)  # type: ignore
    except Review.DoesNotExist:
        raise ReviewNotFound()

    # 2. 좋아요 삭제(deleted_count = 1(삭제)/0(유지))
    deleted_count, _ = ReviewLike.objects.filter(user=user, review=review).delete()  # type: ignore

    if deleted_count > 0:
        review.like_count -= 1
        review.save(update_fields=["like_count"])

    return review.like_count
