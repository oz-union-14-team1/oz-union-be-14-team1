from apps.user.models.user import User

from apps.user.models.preference import Preference

def get_user_preferences(user: User):
    # N+1 문제 방지를 위해 select_related 사용
    return Preference.objects.filter(user=user).select_related('genre')