from typing import Optional

from django.db.models import QuerySet
from apps.community.models.reviews import Review


def get_community_review_all(genre_name: Optional[str] = None) -> QuerySet[Review]:
    """
    커뮤니티용 전체 리뷰 피드를 조회합니다.
    장르 이름(genre)이 전달되면 해당 장르의 게임 리뷰만 필터링합니다.
    """
    # 기본 쿼리셋
    queryset = (
        Review.objects.filter(is_deleted=False)
        .select_related("user", "game")
        .prefetch_related("game__game_genres__genre")
    )

    # 장르 이름으로 필터링 적용
    if genre_name:
        queryset = queryset.filter(game__game_genres__genre__genre=genre_name)
        # 조인으로 인해 발생 가능한 중복데이터 제거
        queryset = queryset.distinct()

    return queryset.order_by("-created_at")
