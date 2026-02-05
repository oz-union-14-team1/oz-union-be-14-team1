import unittest

try:
    from PIL import Image  # type: ignore
except ModuleNotFoundError:
    raise unittest.SkipTest("Pillow(PIL) not installed")

import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# 1. 테스트용 임시 미디어 루트 생성 (실제 폴더 오염 방지)
MEDIA_ROOT = tempfile.mkdtemp()

User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)  # 미디어 경로를 임시 폴더로 변경
class ProfileImageTestCase(APITestCase):

    def setUp(self):
        """테스트 시작 전 실행되는 초기화 함수"""
        # 유저 생성 및 로그인 (토큰 인증 강제 적용)
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.client.force_authenticate(user=self.user)

        self.url = reverse("user:profile_image")

    def tearDown(self):
        """테스트 종료 후 실행되는 정리 함수"""
        # 임시 미디어 폴더 삭제
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def generate_image_file(self):
        """테스트용 더미 이미지 파일 생성 헬퍼 함수"""
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), "white")  # 100x100 흰색 이미지
        image.save(file, "jpeg")
        file.seek(0)
        return SimpleUploadedFile(
            "test_profile.jpg", file.read(), content_type="image/jpeg"
        )

    def test_upload_profile_image_success(self):
        """[POST] 프로필 이미지 업로드 성공 테스트"""
        # Given: 이미지 파일 준비
        image = self.generate_image_file()
        data = {"profile_image": image}

        # When: 업로드 요청 (multipart 형식 필수)
        response = self.client.post(self.url, data, format="multipart")

        # Then: 상태 코드 200 및 DB 업데이트 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # DB에서 최신 정보 다시 가져오기
        self.assertIsNotNone(self.user.profile_img_url)  # URL이 저장되었는지 확인
        self.assertTrue(
            self.user.profile_img_url.startswith("/media/profile_images/")
        )  # 경로 확인

    def test_overwrite_profile_image(self):
        """이미지가 이미 있을 때 덮어쓰기(교체) 테스트"""
        # 1. 첫 번째 업로드
        image1 = self.generate_image_file()
        self.client.post(self.url, {"profile_image": image1}, format="multipart")
        self.user.refresh_from_db()
        first_url = self.user.profile_img_url

        # 2. 두 번째 업로드 (덮어쓰기 시도)
        image2 = self.generate_image_file()
        response = self.client.post(
            self.url, {"profile_image": image2}, format="multipart"
        )

        # 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(
            first_url, self.user.profile_img_url
        )  # URL이 바뀌었는지 확인

    def test_delete_profile_image_success(self):
        """프로필 이미지 삭제 테스트"""
        # Given: 이미지가 있는 상태로 세팅
        self.user.profile_img_url = "/media/profile_images/dummy.jpg"
        self.user.save()

        # When: 삭제 요청
        response = self.client.delete(self.url)

        # Then: 상태 코드 204 및 DB 초기화 확인
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.profile_img_url)  # DB 필드가 NULL인지 확인

    def test_upload_without_authentication(self):
        """비로그인 유저 접근 차단 테스트"""
        self.client.logout()  # 로그아웃
        image = self.generate_image_file()
        response = self.client.post(
            self.url, {"profile_image": image}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
