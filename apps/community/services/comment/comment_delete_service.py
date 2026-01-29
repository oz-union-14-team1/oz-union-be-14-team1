from apps.community.models import ReviewComment
from django.db import transaction


@transaction.atomic
def delete_comment(comment: ReviewComment) -> None:
    """
    이미 조회/검증된 comment 객체를 받아 소프트 삭제(Soft Delete)를 수행
    """
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted"])
