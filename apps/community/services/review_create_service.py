from django.db import transaction
from django.shortcuts import get_object_or_404
from typing import Any
from apps.community.models.reviews import Review
from apps.game.models.game import Game
from apps.user.models.user import User


@transaction.atomic
def create_review(
    *, author: User, game_id: int, validated_data: dict[str, Any]
) -> Review:
    """
    리뷰 생성 비즈니스 로직
    """
    game = get_object_or_404(Game, pk=game_id)

    review = Review.objects.create(  # type: ignore
        user=author,
        game=game,
        content=validated_data["content"],
        rating=validated_data["rating"],
    )

    return review
