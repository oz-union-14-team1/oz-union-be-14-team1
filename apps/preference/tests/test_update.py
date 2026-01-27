from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.preference.models.genre_preference import GenrePreference # 수정됨
from apps.preference.services.preference_service import update_user_total_preferences # 수정됨

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

        GenrePreference.objects.create(user=self.user, genre=self.genre_rpg)

    def test_update_preferences_success(self):
        """기존 장르(RPG)가 삭제되고 새로운 장르(FPS, Action)로 교체되는지 확인"""

        # 1. 초기 상태 확인 (RPG 1개)
        self.assertEqual(GenrePreference.objects.filter(user=self.user).count(), 1)

        # 2. 업데이트 실행 (FPS, Action 으로 교체)
        new_genre_ids = [self.genre_fps.id, self.genre_action.id]
        update_user_total_preferences(self.user, genre_ids=new_genre_ids, tag_ids=[])

        # 3. 결과 검증
        # - 총 개수는 2개가 되어야 함
        self.assertEqual(GenrePreference.objects.filter(user=self.user).count(), 2)
        # - 기존 RPG는 삭제되어야 함
        self.assertFalse(
            GenrePreference.objects.filter(user=self.user, genre=self.genre_rpg).exists()
        )
        # - 새로운 FPS, Action은 존재해야 함
        self.assertTrue(
            GenrePreference.objects.filter(user=self.user, genre=self.genre_fps).exists()
        )

    def test_update_preferences_empty(self):
        """빈 리스트로 업데이트 시 모든 장르가 삭제되는지 확인"""
        update_user_total_preferences(self.user, genre_ids=[], tag_ids=[])
        self.assertEqual(GenrePreference.objects.filter(user=self.user).count(), 0)


class PreferenceUpdateAPIViewTest(TestCase):
    """
    APIView 테스트
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("preference_create")

        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.genre_rpg = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre_fps = Genre.objects.create(Genre="FPS", Genre_ko="총")

        GenrePreference.objects.create(user=self.user, genre=self.genre_rpg)

    def test_update_preference_unauthorized(self):
        """로그인하지 않은 상태로 요청 시 401 에러"""
        data = {"Genres": [self.genre_fps.id]}
        # PUT 메서드는 제거되었으므로 POST 사용
        response = self.client.post(self.url, data, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_update_preference_success(self):
        """로그인 후 정상 수정 (200) 및 데이터 교체 확인"""
        self.client.force_authenticate(user=self.user)

        # RPG -> FPS 로 변경 요청
        data = {"Genres": [self.genre_fps.id]}
        response = self.client.post(self.url, data, format="json")

        # 1. 응답 코드 및 메시지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "저장 완료")

        # 2. DB 데이터 교체 확인
        # RPG는 없고
        self.assertFalse(
            GenrePreference.objects.filter(
                user=self.user, genre_id=self.genre_rpg.id
            ).exists()
        )
        # FPS는 있어야 함
        self.assertTrue(
            GenrePreference.objects.filter(
                user=self.user, genre_id=self.genre_fps.id
            ).exists()
        )