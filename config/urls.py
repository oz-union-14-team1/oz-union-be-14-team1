from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("api/v1/user/", include("apps.user.urls")),
    path("api/v1/user/preference/", include("apps.preference.urls")),
    path("api/v1/community/", include("apps.community.urls")),
    path("api/v1/community/summary/", include("apps.ai.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        # import를 이 블록 안에서 함으로써, 배포 환경에서는 불필요한 import를 막음
        import debug_toolbar
        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [
            # 1. 코드를 읽고 자동으로 스키마를 생성하는 뷰
            path("api/schema", SpectacularAPIView.as_view(), name="schema"),
            # 2. Swagger UI 설정 수정
            path(
                "api/schema/swagger-ui",
                SpectacularSwaggerView.as_view(url_name="schema"),
                name="swagger-ui",
            ),
            path(
                "api/schema/redoc",
                SpectacularRedocView.as_view(url_name="schema"),
                name="redoc",
            ),
        ]
