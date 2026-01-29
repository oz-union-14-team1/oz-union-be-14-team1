from django.db import transaction
from typing import Any

from apps.community.models import ReviewComment


@transaction.atomic
def update_comment(
    *, comment: ReviewComment, validated_data: dict[str, Any]
) -> ReviewComment:

    # 1. 데이터 업데이트
    if "content" in validated_data:
        comment.content = validated_data["content"]
        # 2. 저장
        comment.save(update_fields=["content"])

    return comment  # type: ignore
