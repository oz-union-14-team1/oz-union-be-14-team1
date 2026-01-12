from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    if "drf_spectacular" in settings.INSTALLED_APPS:
        urlpatterns += [

            # YAML이 아닌 코드를 읽고 자동으로 만드는 세팅
            # path("api/schema", SpectacularAPIView.as_view(), name="schema"),
            # path("api/schema/swagger-ui", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

            path('api/schema/swagger-ui', SpectacularSwaggerView.as_view(url='/static/swagger.yaml'),
                 name='swagger-ui'),
            path("api/schema/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        ]