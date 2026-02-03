from rest_framework import serializers


class ProfileImageSerializer(serializers.Serializer):
    profile_image = serializers.ImageField(required=True, write_only=True)

    def validate_profile_image(self, value):
        limit_mb = 5
        if value.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"이미지 크기는 {limit_mb}MB를 초과할 수 없습니다.")
        return value