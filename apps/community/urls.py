from django.urls import path
from .views import (
    GameReviewListCreateView,
    ReviewDetailView,
    CommentListCreateView,
    CommentDetailView,
)

urlpatterns = [
    # 1. 리뷰 등록 및 목록 조회:
    path("<int:game_id>/reviews", GameReviewListCreateView.as_view()),
    # 2. 리뷰 수정 및 삭제:
    path("reviews/<int:review_id>", ReviewDetailView.as_view()),
    # 3. 댓글 작성 및 목록 조회:
    path("reviews/<int:review_id>/comments", CommentListCreateView.as_view()),
    # 4. 댓글 수정 및 삭제:
    path("reviews/comments/<int:comment_id>", CommentDetailView.as_view()),
]
