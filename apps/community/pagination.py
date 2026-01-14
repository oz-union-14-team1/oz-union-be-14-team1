from typing import Any, Optional

from django.db.models import QuerySet
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.views import APIView


class ReviewPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 50

    def paginate_queryset(
        self,
        queryset: QuerySet[Any],
        request: Request,
        view: Optional[APIView] = None,
    ) -> list[Any] | None:
        try:
            # DRF 기본 pagination 로직
            return super().paginate_queryset(queryset, request, view)

        except NotFound:
            page_param = request.query_params.get(self.page_query_param, "1")

            # page 값 자체가 잘못된 경우 → 400
            try:
                page_number = int(page_param)
            except (TypeError, ValueError):
                raise ValidationError("page는 정수여야 합니다.")

            if page_number <= 0:
                raise ValidationError("page는 1 이상이어야 합니다.")

            # page_size 안전 처리 (mypy)
            page_size = self.get_page_size(request)
            if page_size is None:
                return list(queryset)

            paginator = self.django_paginator_class(queryset, page_size)

            # paginator 메타 유지 + 빈 결과
            self.page = paginator.page(paginator.num_pages)
            self.page.object_list = []

            return []
