from apps.community.selectors.review_selector import check_and_get_review_for_update
from apps.user.models.user import User
from django.db import transaction


@transaction.atomic
def delete_review(review_id: int, user: User) -> None:
    review = check_and_get_review_for_update(review_id=review_id, user=user)

    review.is_deleted = True
    review.save(update_fields=["is_deleted"])
