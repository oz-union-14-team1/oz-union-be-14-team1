from rest_framework import serializers
from apps.game.models.wishlist import Wishlist


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["game"]

    def create(self, validated_data):
        user = self.context["request"].user
        game = validated_data["game"]

        wishlist, created = Wishlist.objects.get_or_create(user=user, game=game)

        return wishlist


class WishlistSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source="game.name", read_only=True)
    game_image = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ["id", "game", "game_name", "game_image", "created_at"]

    def get_game_image(self, obj):
        first_image = obj.game.game_images.first()
        if first_image:
            return first_image.img_url
        return None
