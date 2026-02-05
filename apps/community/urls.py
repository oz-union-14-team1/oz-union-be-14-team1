from django.urls import path

from apps.community.views.comment.comment_api import ReviewCommentAPIView
from apps.community.views.comment.comment_update_api import ReviewCommentUpdateAPIView
from apps.community.views.community_api import CommunityReviewListAPIView
from apps.community.views.review.review_api import ReviewAPIView, MyReviewListAPIView
from apps.community.views.review.review_like_api import ReviewLikeAPIView
from apps.community.views.review.review_update_api import ReviewUpdateAPIView

urlpatterns = [
    # community
    path("reviews", CommunityReviewListAPIView.as_view(), name="community_review_all"),
    # review
    path("reviews/me", MyReviewListAPIView.as_view(), name="my_review_list"),
    path("<int:game_id>/reviews", ReviewAPIView.as_view(), name="game_review_create"),
    path(
        "reviews/<int:review_id>", ReviewUpdateAPIView.as_view(), name="review_update"
    ),
    # like
    path(
        "reviews/<int:review_id>/like", ReviewLikeAPIView.as_view(), name="review_like"
    ),
    # comment
    path(
        "reviews/<int:review_id>/comments",
        ReviewCommentAPIView.as_view(),
        name="review_comments",
    ),
    path(
        "reviews/comments/<int:comment_id>",
        ReviewCommentUpdateAPIView.as_view(),
        name="review_comments_update",
    ),
]
