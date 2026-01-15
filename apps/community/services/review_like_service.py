from django.db import transaction

from apps.community.exceptions.review_exceptions import ReviewNotFound
from apps.community.models.reviews import Review
from apps.community.models.review_like import ReviewLike
from apps.user.models.user import User


@transaction.atomic
def create_review_like(user: User, review_id: int) -> tuple[bool, int]:
    # 1. 리뷰 가져오기 (select_for_update로 동시성 제어 - 락 걸기)
    try:
        review = Review.objects.select_for_update().get(id=review_id)  # type: ignore
    except Review.DoesNotExist:
        raise ReviewNotFound()

    # 2. 중간 테이블(ReviewLike) 확인
    like_obj, created = ReviewLike.objects.get_or_create(user=user, review=review)  # type: ignore

    if created:
        # 없어서 새로 생성됨 -> 좋아요 등록
        review.like_count += 1
        is_liked = True
    else:
        # 이미 있어서 가져옴 -> 좋아요 취소
        like_obj.delete()  # 기록 삭제
        review.like_count -= 1
        is_liked = False

    # 3. 변경된 like_count 저장
    review.save()

    # 4. 결과 반환 (현재 상태, 갱신된 총 개수)
    return is_liked, review.like_count
