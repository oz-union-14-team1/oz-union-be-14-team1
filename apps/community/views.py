# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer


# --- 유틸리티: 에러 응답 생성기 ---
def error_response(message, status_code):
    return Response({"error_detail": message}, status=status_code)


# 리뷰 목록 조회 등록
class GameReviewListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, game_id):
        sort = request.query_params.get("sort", "latest")
        reviews = Review.objects.filter(game_id=game_id)

        if sort == "latest":
            reviews = reviews.order_by("-created_at")

        page = int(request.query_params.get("page", 1))
        page_size = 10
        start = (page - 1) * page_size
        end = start + page_size

        serializer = ReviewSerializer(reviews[start:end], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, game_id):
        if not request.user.is_authenticated:
            return error_response(
                "자격 인증 데이터가 제공되지 않았습니다.", status.HTTP_401_UNAUTHORIZED
            )

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(user=request.user, game_id=game_id)
            return Response(
                {"id": review.id, "message": "리뷰가 등록되었습니다."},
                status=status.HTTP_201_CREATED,
            )
        return error_response("이 필드는 필수 항목입니다.", status.HTTP_400_BAD_REQUEST)


# 리뷰 수정 삭제
class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, review_id):
        return get_object_or_404(Review, pk=review_id)

    def put(self, request, review_id):
        review = self.get_object(review_id)
        if review.user != request.user:
            return error_response(
                "작성자가 일치하지 않습니다.", status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            updated_review = serializer.save()
            return Response(
                {"id": updated_review.id, "updated_at": updated_review.updated_at},
                status=status.HTTP_200_OK,
            )
        return error_response("잘못된 요청입니다.", status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        if review.user != request.user:
            return error_response("삭제 권한이 없습니다.", status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(
            {"message": "리뷰가 삭제되었습니다."}, status=status.HTTP_200_OK
        )


# 댓글 목록 조회 및 작성
class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, review_id):
        sort = request.query_params.get("sort", "latest")
        comments = Comment.objects.filter(review_id=review_id)

        if sort == "latest":
            comments = comments.order_by("-created_at")

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, review_id):
        if not request.user.is_authenticated:
            return error_response(
                "자격 인증 데이터가 제공되지 않았습니다.", status.HTTP_401_UNAUTHORIZED
            )

        review = get_object_or_404(Review, pk=review_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(user=request.user, review=review)
            return Response(
                {"id": comment.id, "message": "댓글 등록 성공"},
                status=status.HTTP_201_CREATED,
            )
        return error_response(
            "데이터가 유효하지 않습니다.", status.HTTP_400_BAD_REQUEST
        )


# 댓글 수정 삭제
class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.user != request.user:
            return error_response(
                "작성자가 일치하지 않습니다.", status.HTTP_403_FORBIDDEN
            )

        comment.content = request.data.get("content", comment.content)
        comment.save()

        return Response(
            {"id": comment.id, "updated_at": comment.updated_at},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.user != request.user:
            return error_response("삭제 권한이 없습니다.", status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(
            {"message": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK
        )
