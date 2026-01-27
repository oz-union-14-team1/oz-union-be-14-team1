from django.db import transaction
from typing import List
from apps.user.models.user import User
from apps.preference.models.preference import Preference
from apps.preference.services.preference_service import create_user_preferences


@transaction.atomic()
def update_user_preferences(user: User, genre_ids: List[int]):
    # 1. 기존 선호 장르 전체 삭제
    Preference.objects.filter(user=user).delete()  # type: ignore

    # 2. 새로운 장르 생성 (create 서비스 재활용)
    create_user_preferences(user, genre_ids)
