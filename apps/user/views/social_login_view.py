from django.shortcuts import redirect
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny
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
from apps.user.services.discord_service import DiscordLoginService
from uuid import uuid4


User = get_user_model()


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["소셜 로그인"],
        summary="구글 로그인 콜백",
        description="구글 로그인 후 리디렉션되는 API입니다. 구글 인증 코드(code)를 받아 처리 후 프론트로 리디렉션합니다.",
        parameters=[
            OpenApiParameter(
                name="code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="구글에서 발급받은 인가 코드",
                required=True,
            )
        ],
        responses={
            302: OpenApiResponse(
                description="로그인 성공 후 프론트엔드 URL로 리디렉션 (Query Param으로 token 전달)"
            )
        },
    )
    def get(self, request):
        # 1. 구글이 URL 쿼리 파라미터로 code를 줍니다.
        code = request.GET.get("code")

        redirect_uri = (
            "http://localhost:8000/api/v1/user/google/login"
            if settings.DEBUG
            else "https://swbak.cloud/api/v1/user/google/login"
        )

        if not code:
            return Response(
                {"error": "code가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        front_url = (
            "http://localhost:3000"
            if settings.DEBUG
            else "https://oz-union-fe-14-team1.vercel.app"
        )

        try:
            # 2. 구글 서버 통신 (토큰 & 유저정보 가져오기)
            service = GoogleLoginService(redirect_uri=redirect_uri)
            access_token = service.get_access_token(code)
            google_user_info = service.get_user_info(access_token)

            email = google_user_info.get("email")
            email_verified = google_user_info.get("email_verified")
            social_id = google_user_info.get("sub")

            if not email_verified:
                return redirect(f"{front_url}/login/fail?error=email_not_verified")

            # 3. 회원가입/로그인 로직 (기존과 동일)
            with transaction.atomic():
                social_account = SocialAccount.objects.filter(
                    provider="google", social_id=social_id
                ).first()
                if social_account:
                    user = social_account.user
                else:
                    user = User.objects.filter(email=email).first()
                    if not user:
                        temp_nickname = f"s_{str(uuid4())[:8]}"
                        user = User.objects.create_user(email=email, password=None, nickname=temp_nickname)
                    SocialAccount.objects.create(
                        user=user, provider="google", social_id=social_id
                    )

            # 4. 우리 서비스 토큰 발급
            token_service = TokenService()
            refresh_token, new_access_token = token_service.create_token_pair(user=user)

            response = redirect(f"{front_url}/login/success?token={new_access_token}")

            # 5. Refresh Token은 안전하게 쿠키에 굽기
            set_refresh_cookie(response, refresh_token)

            return response

        except Exception as e:
            return redirect(f"{front_url}/login/fail?error={str(e)}")


class DiscordLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["소셜 로그인"],
        summary="디스코드 로그인 콜백",
        description="디스코드 로그인 후 리디렉션되는 API입니다.",
        parameters=[
            OpenApiParameter(
                name="code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="디스코드 인가 코드",
                required=True,
            )
        ],
    )
    def get(self, request):
        code = request.GET.get("code")

        redirect_uri = (
            "http://localhost:8000/api/v1/user/discord/login"
            if settings.DEBUG
            else "https://swbak.cloud/api/v1/user/discord/login"
        )

        front_url = (
            "http://localhost:3000"
            if settings.DEBUG
            else "https://oz-union-fe-14-team1.vercel.app"
        )

        if not code:
            return Response({"error": "code가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. 디스코드 서비스 호출
            service = DiscordLoginService(redirect_uri=redirect_uri)
            access_token = service.get_access_token(code)
            user_info = service.get_user_info(access_token)

            # 2. 정보 추출
            social_id = user_info.get("id")
            email = user_info.get("email")
            is_verified = user_info.get("verified")  # 이메일 인증 여부 (Boolean)

            # 디스코드 계정에 이메일이 없거나 인증되지 않은 경우 처리
            if not email:
                return redirect(f"{front_url}/login/fail?error=no_email_provided")
            if not is_verified:
                return redirect(f"{front_url}/login/fail?error=email_not_verified")

            # 3. 회원가입/로그인 로직 (구글과 동일 패턴)
            with transaction.atomic():
                # 이미 디스코드 계정으로 가입된 유저인지 확인
                social_account = SocialAccount.objects.filter(
                    provider="discord", social_id=social_id
                ).first()

                if social_account:
                    user = social_account.user
                else:
                    # 기존 이메일 유저와 연동 확인
                    user = User.objects.filter(email=email).first()
                    if not user:
                        temp_nickname = f"s_{str(uuid4())[:8]}"
                        # 신규 유저 생성
                        user = User.objects.create_user(email=email, password=None,nickname=temp_nickname)

                    # 소셜 계정 연동 생성
                    SocialAccount.objects.create(
                        user=user, provider="discord", social_id=social_id
                    )

            # 4. JWT 토큰 발급
            token_service = TokenService()
            refresh_token, new_access_token = token_service.create_token_pair(user=user)

            # 5. 리다이렉트
            response = redirect(f"{front_url}/login/success?token={new_access_token}")
            set_refresh_cookie(response, refresh_token)

            return response

        except Exception as e:
            return redirect(f"{front_url}/login/fail?error={str(e)}")