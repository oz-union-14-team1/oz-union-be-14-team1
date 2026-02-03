from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.user.serializers.profile_img import ProfileImageSerializer
from apps.user.services.profile_img_service import ProfileImageService


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # 필수

    @extend_schema(
        tags=["프로필"], summary="프로필이미지 업로드", request=ProfileImageSerializer
    )
    def post(self, request):
        # 1. 입력 데이터 검증
        serializer = ProfileImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. 서비스 호출
        service = ProfileImageService()

        image_url = service.update_profile_image(
            user=request.user,
            image_file=serializer.validated_data['profile_image']
        )

        return Response(
            {
                "message": "프로필 사진이 등록되었습니다.",
                "profile_img_url": image_url
            },
            status=status.HTTP_200_OK
        )