from typing import Any

from apps.community.models.reviews import Review


def update_review(*, review: Review, validated_data: dict[str, Any]) -> Review:
    """
    Selector를 통해 검증된 리뷰 객체를 가져와서
    실제 필드 업데이트와 저장을 수행합니다.
    """

    # 1. 데이터 업데이트
    for field in ("content", "rating"):
        if field in validated_data:
            setattr(review, field, validated_data[field])

    # 2. 저장
    review.save()

    return review
