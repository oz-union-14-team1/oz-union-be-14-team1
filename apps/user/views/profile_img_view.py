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
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(tags=["프로필"], summary="프로필 이미지 조회")
    def get(self, request):
        user_profile_url = request.user.profile_img_url

        # 상대 경로(예: /media/...)인 경우 도메인을 붙여서 완전한 URL로 변환
        if user_profile_url and not user_profile_url.startswith("http"):
            user_profile_url = request.build_absolute_uri(user_profile_url)

        return Response(
            {"profile_img_url": user_profile_url},
            status=status.HTTP_200_OK,
        )

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
            user=request.user, image_file=serializer.validated_data["profile_image"], request=request
        )

        # 응답할 때 도메인을 붙여서 완전한 URL로 변환하여 전달
        if image_url and not image_url.startswith("http"):
            full_image_url = request.build_absolute_uri(image_url)
        else:
            full_image_url = image_url

        return Response(
            {
                "message": "프로필 사진이 등록되었습니다.",
                "profile_img_url": full_image_url,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(tags=["프로필"], summary="프로필 이미지 삭제")
    def delete(self, request):
        # 1. 서비스 호출
        service = ProfileImageService()

        service.delete_profile_image(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
