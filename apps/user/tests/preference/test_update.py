from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.user.models.preference import Preference
from apps.user.services.preference.preference_update_service import (
    update_user_preferences,
)

User = get_user_model()


class PreferenceUpdateServiceTest(TestCase):
    """
    서비스 레이어 테스트
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.genre_rpg = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre_fps = Genre.objects.create(Genre="FPS", Genre_ko="총")
        self.genre_action = Genre.objects.create(Genre="Action", Genre_ko="액션")

        Preference.objects.create(user=self.user, genre=self.genre_rpg)

    def test_update_preferences_success(self):
        """기존 장르(RPG)가 삭제되고 새로운 장르(FPS, Action)로 교체되는지 확인"""

        # 1. 초기 상태 확인 (RPG 1개)
        self.assertEqual(Preference.objects.filter(user=self.user).count(), 1)
        self.assertTrue(
            Preference.objects.filter(user=self.user, genre=self.genre_rpg).exists()
        )

        # 2. 업데이트 실행 (FPS, Action 으로 교체)
        new_genre_ids = [self.genre_fps.id, self.genre_action.id]
        update_user_preferences(self.user, new_genre_ids)

        # 3. 결과 검증
        # - 총 개수는 2개가 되어야 함
        self.assertEqual(Preference.objects.filter(user=self.user).count(), 2)
        # - 기존 RPG는 삭제되어야 함
        self.assertFalse(
            Preference.objects.filter(user=self.user, genre=self.genre_rpg).exists()
        )
        # - 새로운 FPS, Action은 존재해야 함
        self.assertTrue(
            Preference.objects.filter(user=self.user, genre=self.genre_fps).exists()
        )
        self.assertTrue(
            Preference.objects.filter(user=self.user, genre=self.genre_action).exists()
        )

    def test_update_preferences_empty(self):
        """빈 리스트로 업데이트 시 모든 장르가 삭제되는지 확인 (로직 허용 시)"""
        update_user_preferences(self.user, [])
        self.assertEqual(Preference.objects.filter(user=self.user).count(), 0)


class PreferenceUpdateAPIViewTest(TestCase):
    """
    APIView 테스트
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:preference_create")

        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.genre_rpg = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre_fps = Genre.objects.create(Genre="FPS", Genre_ko="총")

        Preference.objects.create(user=self.user, genre=self.genre_rpg)

    def test_update_preference_unauthorized(self):
        """로그인하지 않은 상태로 요청 시 401 에러"""
        data = {"genre_ids": [self.genre_fps.id]}
        response = self.client.put(self.url, data, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_update_preference_success(self):
        """로그인 후 정상 수정 (200) 및 데이터 교체 확인"""
        self.client.force_authenticate(user=self.user)

        # RPG -> FPS 로 변경 요청
        data = {"genre_ids": [self.genre_fps.id]}
        response = self.client.put(self.url, data, format="json")

        # 1. 응답 코드 및 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "수정 완료")

        # 2. DB 데이터 교체 확인
        # RPG는 없고
        self.assertFalse(
            Preference.objects.filter(
                user=self.user, genre_id=self.genre_rpg.id
            ).exists()
        )
        # FPS는 있어야 함
        self.assertTrue(
            Preference.objects.filter(
                user=self.user, genre_id=self.genre_fps.id
            ).exists()
        )

    def test_update_preference_invalid_data(self):
        """잘못된 데이터 요청 (400)"""
        self.client.force_authenticate(user=self.user)

        # 존재하지 않는 장르 ID
        data = {"genre_ids": [9999]}
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 실패 시 기존 데이터(RPG)가 유지되는지도 확인하면 더 완벽함
        self.assertTrue(
            Preference.objects.filter(
                user=self.user, genre_id=self.genre_rpg.id
            ).exists()
        )
