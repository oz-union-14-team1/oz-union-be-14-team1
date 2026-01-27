from django.db import transaction

from apps.preference.models import TagPreference, GenrePreference
from apps.user.models.user import User


@transaction.atomic
def update_user_total_preferences(user: User, tag_ids: list[int], genre_ids: list[int]):
    # 1. 기존 데이터 삭제 (초기화)
    GenrePreference.objects.filter(user=user).delete()
    TagPreference.objects.filter(user=user).delete()

    # 2. 장르 생성
    if genre_ids:
        genre_objs = [GenrePreference(user=user, genre_id=gid) for gid in genre_ids]
        GenrePreference.objects.bulk_create(genre_objs)

    # 3. 태그 생성
    if tag_ids:
        tag_objs = [TagPreference(user=user, tag_id=tid) for tid in tag_ids]
        TagPreference.objects.bulk_create(tag_objs)
