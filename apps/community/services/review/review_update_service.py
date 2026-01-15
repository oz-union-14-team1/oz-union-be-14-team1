from django.db import transaction
from typing import Any

from apps.community.models.reviews import Review
from apps.user.models.user import User
from apps.community.selectors.review_selector import check_and_get_review_for_update


@transaction.atomic
def update_review(
    *, user: User, review_id: int, validated_data: dict[str, Any]
) -> Review:
    """
    Selector를 통해 검증된 리뷰 객체를 가져와서
    실제 필드 업데이트와 저장을 수행합니다.
    """
    update_fields: list[str] = []

    # 1. Selector 호출 (문제가 있다면 여기서 예외가 발생하여 중단)
    review = check_and_get_review_for_update(review_id=review_id, user=user)

    # 2. 데이터 업데이트
    for field in ("content", "rating"):
        if field in validated_data:
            setattr(review, field, validated_data[field])
            update_fields.append(field)

    # 3. 저장
    review.save()

    return review
