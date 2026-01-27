from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.preference.models.genre_preference import GenrePreference  # 수정됨
from apps.preference.serializers.preference_create import UserPreferenceSerializer
from apps.preference.services.preference_service import (
    update_user_total_preferences,
)  # 수정됨

User = get_user_model()


class PreferenceSerializerTest(TestCase):
    def setUp(self):
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

    def test_validate_success(self):
        """정상적인 데이터 입력"""
        # genre_ids -> Genres 로 필드명 변경
        data = {"Genres": [self.genre1.id, self.genre2.id]}
        serializer = UserPreferenceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # 중복 제거 및 리스트 반환 확인
        self.assertEqual(
            set(serializer.validated_data["Genres"]),
            {self.genre1.id, self.genre2.id},
        )

    def test_validate_empty_list_allowed(self):
        """빈 리스트 입력 허용 (allow_empty=True)"""
        data = {"Genres": []}
        serializer = UserPreferenceSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_fail_invalid_genre_id(self):
        """존재하지 않는 장르 ID 입력 시 에러"""
        invalid_id = 9999
        data = {"Genres": [self.genre1.id, invalid_id]}
        serializer = UserPreferenceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "존재하지 않는 장르가 포함되어 있습니다.",
            str(serializer.errors["Genres"]),
        )


class PreferenceServiceTest(TestCase):
    """
    비즈니스 로직 테스트
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

    def test_create_preferences_success(self):
        """선호 장르 일괄 생성"""
        genre_ids = [self.genre1.id, self.genre2.id]
        # create -> update_user_total_preferences (통합 서비스) 사용
        update_user_total_preferences(self.user, genre_ids=genre_ids, tag_ids=[])

        self.assertEqual(GenrePreference.objects.filter(user=self.user).count(), 2)


class PreferenceAPIViewTest(TestCase):
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

    def test_create_preference_unauthorized(self):
        """로그인하지 않은 상태로 요청 시 401 에러"""
        data = {"Genres": [self.genre1.id]}
        response = self.client.post(self.url, data, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_create_preference_success(self):
        """로그인 후 정상 등록 (200 OK)"""
        self.client.force_authenticate(user=self.user)

        data = {"Genres": [self.genre1.id, self.genre2.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "저장 완료")

        # DB 확인
        self.assertTrue(
            GenrePreference.objects.filter(
                user=self.user, genre_id=self.genre1.id
            ).exists()
        )
        self.assertTrue(
            GenrePreference.objects.filter(
                user=self.user, genre_id=self.genre2.id
            ).exists()
        )

    def test_create_preference_invalid_data(self):
        """잘못된 데이터 요청 (400)"""
        self.client.force_authenticate(user=self.user)

        # 존재하지 않는 장르 ID
        data = {"Genres": [9999]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
