from django.db import transaction
from typing import Any

from apps.community.models import ReviewComment
from apps.community.selectors.comment_selector import check_and_get_comment_for_update
from apps.user.models.user import User


@transaction.atomic
def update_comment(
    *, user: User, comment_id: int, validated_data: dict[str, Any]
) -> ReviewComment:

    # 1. Selector 호출 (문제가 있다면 여기서 예외가 발생하여 중단)
    comment = check_and_get_comment_for_update(comment_id=comment_id, user=user)

    # 2. 데이터 업데이트
    if "content" in validated_data:
        comment.content = validated_data["content"]
        # 3. 저장
        comment.save(update_fields=["content"])

    return comment  # type: ignore
