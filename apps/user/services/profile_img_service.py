from django.core.files.storage import default_storage
import uuid
import os
from django.conf import settings


class ProfileImageService:
    def delete_existing_image(self, user):
        """
        기존 프로필 이미지가 존재한다면 삭제
        :param user:
        :return:
        """
        if user.profile_img_url:
            try:
                media_url = settings.MEDIA_URL
                # URL이 MEDIA_URL로 시작하는 경우에만 경로 추출 시도
                if user.profile_img_url.startswith(media_url):
                    path = user.profile_img_url.replace(media_url, "", 1)

                    if default_storage.exists(path):
                        default_storage.delete(path)
            except Exception:
                pass

    def update_profile_image(self, user, image_file):
        """
        프로필 이미지를 등록합니다.
        """
        # 1. 기존 이미지가 있다면 삭제
        self.delete_existing_image(user)

        # 2. 파일명 난수화
        ext = os.path.splitext(image_file.name)[1]  # .jpg, .png 등 확장자 추출
        new_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"profile_images/{new_filename}"

        # 3. 파일 저장
        saved_path = default_storage.save(file_path, image_file)
        image_url = default_storage.url(saved_path)

        # 4. DB 업데이트
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
