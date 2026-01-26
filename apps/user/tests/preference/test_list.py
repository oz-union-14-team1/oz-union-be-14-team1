from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.user.models.preference import Preference
from apps.user.serializers.preference.preference_list import (
    UserPreferenceListSerializer,
)
from apps.user.services.preference_list_service import get_user_preferences

User = get_user_model()


class PreferenceListServiceTest(TestCase):
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
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

        # 선호 장르 데이터 생성
        Preference.objects.create(user=self.user, genre=self.genre1)
        Preference.objects.create(user=self.user, genre=self.genre2)

    def test_get_user_preferences(self):
        """유저의 선호 장르 목록을 정상적으로 조회하는지 확인"""
        preferences = get_user_preferences(self.user)

        self.assertEqual(preferences.count(), 2)
        self.assertEqual(preferences[0].genre.Genre, "RPG")
        self.assertEqual(preferences[1].genre.Genre, "FPS")


class PreferenceListSerializerTest(TestCase):
    """
    시리얼라이저 테스트
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.genre = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.preference = Preference.objects.create(user=self.user, genre=self.genre)

    def test_serializer_output_format(self):
        """Serializer가 모델 데이터를 원하는 JSON 필드명으로 변환하는지 확인"""
        serializer = UserPreferenceListSerializer(instance=self.preference)
        data = serializer.data

        # 기대하는 필드값 확인 (source='genre.xxx' 매핑 확인)
        self.assertEqual(data["id"], self.genre.id)
        self.assertEqual(data["name"], "RPG")
        self.assertEqual(data["name_ko"], "모험")


class PreferenceListAPIViewTest(TestCase):
    """
    PreferenceAPIView (GET) 통합 테스트
    """

    def setUp(self):
        self.client = APIClient()
        # 주의: urls.py에서 name="preference_create" 하나로 등록되어 있어 GET 요청도 같은 URL 이름을 사용합니다.
        self.url = reverse("user:preference_create")

        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

    def test_get_preference_list_unauthorized(self):
        """로그인하지 않은 상태로 조회 시 401 에러"""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_get_preference_list_success(self):
        """로그인 후 정상 조회 (데이터가 있는 경우)"""
        # 데이터 준비
        Preference.objects.create(user=self.user, genre=self.genre1)
        Preference.objects.create(user=self.user, genre=self.genre2)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # 첫 번째 데이터 검증 (정렬 순서에 따라 인덱스는 다를 수 있음)
        rpg_data = next((item for item in response.data if item["name"] == "RPG"), None)
        self.assertIsNotNone(rpg_data)
        self.assertEqual(rpg_data["name_ko"], "모험")

    def test_get_preference_list_empty(self):
        """선호 장르가 없을 때 빈 리스트 반환"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
