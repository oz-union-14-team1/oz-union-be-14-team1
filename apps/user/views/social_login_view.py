from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.user.models.social import SocialAccount
from apps.user.services.google_service import GoogleLoginService
from apps.user.utils.tokens import TokenService
from apps.user.utils.cookies import set_refresh_cookie

User = get_user_model()


class GoogleLoginView(APIView):
    @extend_schema(
        tags=["소셜 로그인"],
        summary="구글 로그인",
        description="구글 인가 코드(code)를 받아 JWT 토큰을 발급하고 유저를 로그인/가입 시킵니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "구글에서 받은 인가 코드"},
                    "redirect_uri": {"type": "string", "description": "설정한 리디렉션 URI"}
                },
                "required": ["code", "redirect_uri"],
            }
        },
        responses={200: OpenApiResponse(description="로그인 성공 (Access Token 반환)")}
    )
    def get(self, request):  # <--- POST가 아니라 GET입니다!
        # 1. 구글이 URL 쿼리 파라미터로 code를 줍니다.
        code = request.GET.get('code')

        # ⚠️ 중요: 이 주소는 구글 콘솔에 등록한 '승인된 리디렉션 URI'와 토씨 하나 안 틀리고 똑같아야 합니다.
        # 개발/배포 환경에 따라 달라지므로 settings나 env에서 가져오는 게 좋습니다.
        # 예시로 하드코딩 했으나, 실제로는 request.build_absolute_uri() 등을 활용하거나 환경변수로 쓰세요.
        redirect_uri = "http://localhost:8000/users/google/login/" if settings.DEBUG else "https://swbak.cloud/users/google/login/"

        if not code:
            return Response({"error": "code가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        service = GoogleLoginService(redirect_uri=redirect_uri)

        try:
            # 2. 구글 서버 통신 (토큰 & 유저정보 가져오기)
            access_token = service.get_access_token(code)
            google_user_info = service.get_user_info(access_token)

            email = google_user_info.get('email')
            email_verified = google_user_info.get('email_verified')
            social_id = google_user_info.get('sub')

            if not email_verified:
                return Response({"error": "이메일 인증이 안 된 구글 계정입니다."}, status=400)

            # 3. 회원가입/로그인 로직 (기존과 동일)
            with transaction.atomic():
                social_account = SocialAccount.objects.filter(provider='google', social_id=social_id).first()
                if social_account:
                    user = social_account.user
                else:
                    user = User.objects.filter(email=email).first()
                    if not user:
                        user = User.objects.create_user(email=email, password=None)
                    SocialAccount.objects.create(user=user, provider='google', social_id=social_id)

            # 4. 우리 서비스 토큰 발급
            token_service = TokenService()
            refresh_token, new_access_token = token_service.create_token_pair(user=user)

            # 5. [핵심] 프론트엔드로 다시 보내주기 (Redirect)
            # 백엔드가 처리를 다 했으니, 프론트 메인 페이지(3000번)로 돌려보냅니다.
            # 이때 Access Token을 쿼리 파라미터로 붙여서 줍니다.

            front_url = "http://localhost:3000" if settings.DEBUG else "https://oz-union-fe-14-team1.vercel.app"
            response = redirect(f"{front_url}/login/success?token={new_access_token}")  # 프론트가 이 주소에서 토큰을 낚아채야 함

            # 6. Refresh Token은 안전하게 쿠키에 굽기
            set_refresh_cookie(response, refresh_token)

            return response

        except Exception as e:
            # 에러 나면 프론트 에러 페이지로 리디렉션
            front_url = "http://localhost:3000" if settings.DEBUG else "https://oz-union-fe-14-team1.vercel.app"
            return redirect(f"{front_url}/login/fail?error={str(e)}")