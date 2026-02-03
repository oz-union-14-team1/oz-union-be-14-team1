from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import os
from django.conf import settings

class ProfileImageService:
    def update_profile_image(self, user, image_file):
        # 1. 기존 이미지가 있다면 삭제
        if user.profile_img_url:
            try:
                media_url = settings.MEDIA_URL
                # URL이 MEDIA_URL로 시작하는 경우에만 경로 추출 시도
                if user.profile_img_url.startswith(media_url):
                    path = user.profile_img_url.replace(media_url, '', 1)

                    if default_storage.exists(path):
                        default_storage.delete(path)
            except Exception:
                pass

        # 2. 파일명 난수화
        ext = os.path.splitext(image_file.name)[1]  # .jpg, .png 등 확장자 추출
        new_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"profile_images/{new_filename}"

        # 3. 파일 저장
        saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
        image_url = default_storage.url(saved_path)

        # 4. DB 업데이트
        user.profile_img_url = image_url
        user.save(update_fields=['profile_img_url'])

        return image_url
