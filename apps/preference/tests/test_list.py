from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.preference.models.genre_preference import GenrePreference  # 수정됨
from apps.preference.serializers.preference_list import GenreInfoSerializer  # 수정됨
from apps.preference.services.preference_list_service import (
    get_user_total_preferences,
)  # 수정됨

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
        GenrePreference.objects.create(user=self.user, genre=self.genre1)
        GenrePreference.objects.create(user=self.user, genre=self.genre2)

    def test_get_user_preferences(self):
        """유저의 선호 장르 목록을 정상적으로 조회하는지 확인"""
        # get_user_total_preferences는 {"Tags": [], "Genres": []} 형태의 dict를 반환함
        preferences = get_user_total_preferences(self.user)

        genres = preferences["Genres"]
        self.assertEqual(len(genres), 2)
        self.assertEqual(genres[0].Genre, "RPG")
        self.assertEqual(genres[1].Genre, "FPS")


class PreferenceListSerializerTest(TestCase):
    """
    시리얼라이저 테스트
    """

    def setUp(self):
        self.genre = Genre.objects.create(Genre="RPG", Genre_ko="모험")

    def test_serializer_output_format(self):
        """Serializer가 모델 데이터를 원하는 JSON 필드명으로 변환하는지 확인"""
        serializer = GenreInfoSerializer(instance=self.genre)
        data = serializer.data

        # GenreInfoSerializer는 'id'와 'label' 필드를 가짐
        self.assertEqual(data["id"], self.genre.id)
        self.assertEqual(data["label"], "RPG")


class PreferenceListAPIViewTest(TestCase):
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
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

    def test_get_preference_list_unauthorized(self):
        """로그인하지 않은 상태로 조회 시 401 에러"""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_get_preference_list_success(self):
        """로그인 후 정상 조회 (데이터가 있는 경우)"""
        GenrePreference.objects.create(user=self.user, genre=self.genre1)
        GenrePreference.objects.create(user=self.user, genre=self.genre2)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 구조 확인 {"Tags": [], "Genres": []}
        self.assertIn("Genres", response.data)
        self.assertEqual(len(response.data["Genres"]), 2)

        # 데이터 검증
        rpg_data = next(
            (item for item in response.data["Genres"] if item["label"] == "RPG"), None
        )
        self.assertIsNotNone(rpg_data)

    def test_get_preference_list_empty(self):
        """선호 장르가 없을 때 빈 리스트 반환"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Genres"], [])
        self.assertEqual(response.data["Tags"], [])
