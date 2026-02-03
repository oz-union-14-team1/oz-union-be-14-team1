"""
Django settings for oz_playtype project.
"""

import os
import sys
from pathlib import Path
import environ  # type: ignore
import sentry_sdk

# 1. BASE_DIR 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 환경변수 로딩
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# 3. 시크릿 키 & 디버그 (.env 사용)
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
RAWG_API_KEY = env("RAWG_API_KEY", default="dummy_api_key_for_ci")

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "user.User"

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "drf_spectacular",
    "debug_toolbar",
    "corsheaders",
]

CUSTOM_APPS: list[str] = [
    "apps.user",
    "apps.game",
    "apps.ai",
    "apps.community",
    "apps.preference",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Redis 사용 여부
USE_REDIS: bool = env.bool("USE_REDIS", default=False)

# Redis Cache 설정
if USE_REDIS:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env(
                "REDIS_URL",
                default="redis://redis:6379/0",
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "playtype",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# 세션을 Redis에 저장
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# verification settings
VERIFICATION_DEFAULT_TTL_SECONDS: int = int(
    os.getenv("VERIFICATION_DEFAULT_TTL_SECONDS", "300")
)
VERIFICATION_TOKEN_GENERATE_MAX_ATTEMPTS: int = int(
    os.getenv("VERIFICATION_TOKEN_GENERATE_MAX_ATTEMPTS", "5")
)
PASSWORD_RESET_RETURN_CODE = DEBUG
VERIFICATION_CODE_LENGTH: int = int(os.getenv("VERIFICATION_CODE_LENGTH", "6"))
VERIFICATION_TOKEN_BYTES: int = int(os.getenv("VERIFICATION_TOKEN_BYTES", "32"))
VERIFICATION_CODE_CHARS: str = os.getenv("VERIFICATION_CODE_CHARS", "1234567890")

# Telnyx (SMS)
TELNYX_API_KEY: str = env("TELNYX_API_KEY", default="")
TELNYX_FROM_NUMBER: str = env("TELNYX_FROM_NUMBER", default="")

WSGI_APPLICATION = "config.wsgi.application"

# 4. Database 설정 (.env 사용)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 5. 한국 설정
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# 6. Ai 설정(.env)
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
AI_SUMMARY_MIN_REVIEW_COUNT = 10  # 요약 생성 최소 리뷰 수
AI_SUMMARY_UPDATE_INTERVAL_DAYS = 30  # 요약 갱신 주기 (일)
AI_REVIEW_MIN_LENGTH = 10  # 요약에 사용할 리뷰의 최소 글자 수
AI_SUMMARY_MIN_VALID_REVIEWS = 3  # 유효한 리뷰의 개수
AI_SUMMARY_REVIEW_COUNT = 5  # AI에게 요약 자료로 보낼 최대 리뷰 개수
DISABLE_AI_SUMMARY_SIGNAL = False

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# 프로젝트 루트의 'static' 폴더를 정적 파일 경로로 인식시킴
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    # DRF가 스키마(문서) 생성기로 spectacular를 쓰도록 지정
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.BasicAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        "apps.user.utils.authentication.BlacklistJWTAuthentication",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.handler.custom_exception_handler",
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# drf-spectacular 관련 설정
SPECTACULAR_SETTINGS = {
    "TITLE": "오즈 코딩 스쿨 Backend API",
    "DESCRIPTION": "오즈 코딩 스쿨의 웹 사이트 개발을 위한 API입니다.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": """{
        "dom_id": "#swagger-ui",
        "layout": "StandaloneLayout",
        "deepLinking": true,
        "persistAuthorization": true,
        "displayOperationId": true,
        "filter": true,
        
        "urls": [
            {url: "/static/swagger.yaml", name: "1. 기획서 (Static YAML)"},
            {url: "/api/schema", name: "2. 실제 구현 코드 (Live Schema)"}
        ],
        
        "presets": [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ]
    }""",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "SECURITY": [{"BearerAuth": []}],
}

APPEND_SLASH = False

# Celery 설정
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]

if "test" in sys.argv:
    DISABLE_AI_SUMMARY_SIGNAL = True

INTERNAL_IPS = [
    "127.0.0.1",
]

# import socket
#
# try:
#     hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
#     INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
# except Exception:
#     pass


sentry_sdk.init(
    dsn="https://6ba8a2247abb4eafd2f10109756d1374@o4510793767190528.ingest.us.sentry.io/4510793768239104",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    traces_sample_rate=1.0,
)

if DEBUG:
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: "test" not in sys.argv,
        # 테스트 실행 중일 때 툴바 에러 무시하기
        "IS_RUNNING_TESTS": False,
    }
