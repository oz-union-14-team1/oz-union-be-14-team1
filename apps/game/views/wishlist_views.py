from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.game.models.wishlist import Wishlist
from apps.game.serializers.wishlist_serializer import WishlistCreateSerializer,WishlistSerializer


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlists = Wishlist.objects.filter(user=request.user).order_by("-created_at")
        serializer = WishlistSerializer(wishlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WishlistCreateSerializer(data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            wishlist = serializer.save()
            response_serializer = WishlistSerializer(wishlist)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            wishlist = Wishlist.objects.get(pk=pk, user=request.user)
            wishlist.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response(
                {"detail": "위시리스트 항목을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
