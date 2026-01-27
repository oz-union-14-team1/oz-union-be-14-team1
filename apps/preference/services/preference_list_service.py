from apps.preference.models import GenrePreference, TagPreference
from apps.user.models import User


def get_user_total_preferences(user: User):
    # 장르 가져오기 (Genre 객체만 추출)
    genres = [
        p.genre
        for p in GenrePreference.objects.filter(user=user).select_related("genre")
    ]

    # 태그 가져오기 (Tag 객체만 추출)
    tags = [
        t.tag for t in TagPreference.objects.filter(user=user).select_related("tag")
    ]

    return {"Tags": tags, "Genres": genres}
