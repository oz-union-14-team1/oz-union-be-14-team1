from apps.user.models.preference import Preference


def create_user_preferences(user, genre_ids: list[int]):
    """
    유저의 선호 장르를 일괄 생성합니다.
    이 함수는 API와 독립적으로 어디서든 호출 가능합니다.
    """
    preferences = [
        Preference(user=user, genre_id=genre_id)
        for genre_id in genre_ids
    ]
    return Preference.objects.bulk_create(preferences, ignore_conflicts=True)

