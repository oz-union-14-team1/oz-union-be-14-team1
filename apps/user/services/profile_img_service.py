from django.core.files.storage import default_storage
import uuid
import os
from django.conf import settings
from urllib.parse import urlparse

class ProfileImageService:
    def delete_existing_image(self, user):
        """
        기존 프로필 이미지가 존재한다면 삭제
        """
        if user.profile_img_url:
            try:
                # DB에 저장된 값이 절대 경로(http...)일 경우 상대 경로(/media/...)만 추출
                target_url = user.profile_img_url
                if target_url.startswith("http"):
                    parsed = urlparse(target_url)
                    target_url = parsed.path  # 도메인 제외하고 /media/... 부분만 가져옴

                media_url = settings.MEDIA_URL

                # URL이 MEDIA_URL(/media/)로 시작하는 경우에만 실제 파일 경로 추출 시도
                if target_url.startswith(media_url):
                    path = target_url.replace(media_url, "", 1)

                    if default_storage.exists(path):
                        default_storage.delete(path)
            except Exception:
                pass

    def update_profile_image(self, user, image_file, request=None):
        """
        프로필 이미지를 등록합니다.
        """
        # 1. 기존 이미지가 있다면 삭제
        self.delete_existing_image(user)

        # 2. 파일명 난수화
        ext = os.path.splitext(image_file.name)[1]
        new_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"profile_images/{new_filename}"

        # 3. 파일 저장 (물리적 저장)
        saved_path = default_storage.save(file_path, image_file)
        image_url = default_storage.url(saved_path)  # 여기선 /media/... 만 나옴

        # request가 전달되었다면 도메인을 붙여서 절대 경로로 변환
        if request:
            image_url = request.build_absolute_uri(image_url)

        # 4. DB 업데이트 (이제 도메인 포함된 주소가 저장됨)
        user.profile_img_url = image_url
        user.save(update_fields=["profile_img_url"])

        return image_url

    def delete_profile_image(self, user):
        """
        프로필 이미지를 삭제하여 기본이미지로 전환
        """
        # 1. 이미지 삭제
        self.delete_existing_image(user)

        # 2. DB 필드 초기화
        user.profile_img_url = None
        user.save(update_fields=["profile_img_url"])
