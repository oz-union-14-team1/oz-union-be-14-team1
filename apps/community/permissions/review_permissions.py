from rest_framework import permissions

from apps.community.exceptions.review_exceptions import NotReviewAuthor


class IsReviewAuthor(permissions.BasePermission):
    """
    작성자 본인만 수정/삭제 권한을 가짐
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.user != request.user:
            raise NotReviewAuthor()

        return True
