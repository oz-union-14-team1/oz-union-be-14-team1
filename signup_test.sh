set -euo pipefail

DJANGO_CONTAINER="PlayType_Django"

read -p "이메일을 입력하세요: " EMAIL
read -s -p "비밀번호를 입력하세요: " PASSWORD
echo ""

docker exec -i "$DJANGO_CONTAINER" python manage.py shell -c "
from apps.user.models import User
email='''$EMAIL'''.strip().lower()
pw='''$PASSWORD'''

if User.objects.filter(email=email).exists():
    print('이미 존재하는 이메일입니다:', email)
else:
    user = User.objects.create_user(
        email=email,
        password=pw,
    )
    print('생성 완료:', user.id, user.email)
"