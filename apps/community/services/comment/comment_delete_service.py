from apps.community.selectors.comment_selector import check_and_get_comment_for_update
from apps.user.models.user import User
from django.db import transaction


@transaction.atomic
def delete_comment(comment_id: int, user: User) -> None:
    comment = check_and_get_comment_for_update(comment_id=comment_id, user=user)

    comment.is_deleted = True
    comment.save(update_fields=["is_deleted"])
