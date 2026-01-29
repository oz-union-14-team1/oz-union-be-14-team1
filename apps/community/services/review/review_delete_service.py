from django.db import transaction
from apps.community.models.reviews import Review


@transaction.atomic
def delete_review(review: Review) -> None:
    """
    이미 조회/검증된 review 객체를 받아 소프트 삭제(Soft Delete)를 수행
    """
    review.is_deleted = True
    review.save(update_fields=["is_deleted"])
