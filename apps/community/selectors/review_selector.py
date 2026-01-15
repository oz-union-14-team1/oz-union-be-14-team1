from apps.community.models.reviews import Review
from apps.community.exceptions.review_exceptions import ReviewNotFound, NotReviewAuthor
from apps.user.models.user import User


def check_and_get_review_for_update(review_id: int, user: User) -> Review:
    """
    리뷰 조회 및 권한 검증 Selector
    존재하지 않거나 권한이 없으면 예외를 발생시킴
    """
    try:
        # 1. 리뷰 조회
        review = Review.objects.select_for_update().get(id=review_id)  # type: ignore
    except Review.DoesNotExist:
        # 2. 존재 여부 판단 -> 실패 시 404 예외 발생
        raise ReviewNotFound()

    # 3. 작성자 본인 확인 -> 실패 시 403 예외 발생
    if review.user != user:
        raise NotReviewAuthor()

    return review
