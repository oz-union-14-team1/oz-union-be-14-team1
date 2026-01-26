from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.game.models.genre import Genre
from apps.user.models.preference import Preference
from apps.user.serializers.preference.preference_create import UserPreferenceSerializer
from apps.user.services.preference.preference_service import create_user_preferences

User = get_user_model()


class PreferenceSerializerTest(TestCase):
    def setUp(self):
        # 테스트용 장르 데이터 생성
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

    def test_validate_success(self):
        """정상적인 데이터 입력"""
        data = {"genre_ids": [self.genre1.id, self.genre2.id]}
        serializer = UserPreferenceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        # 중복 제거 및 리스트 반환 확인
        self.assertEqual(
            set(serializer.validated_data["genre_ids"]),
            {self.genre1.id, self.genre2.id},
        )

    def test_validate_fail_empty_list(self):
        """빈 리스트 입력 시 에러"""
        data = {"genre_ids": []}
        serializer = UserPreferenceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "최소 하나의 장르를 선택해야 합니다.", str(serializer.errors["genre_ids"])
        )

    def test_validate_fail_invalid_genre_id(self):
        """존재하지 않는 장르 ID 입력 시 에러"""
        invalid_id = 9999
        data = {"genre_ids": [self.genre1.id, invalid_id]}
        serializer = UserPreferenceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "존재하지 않는 장르가 포함되어 있습니다.",
            str(serializer.errors["genre_ids"]),
        )

    def test_validate_deduplication(self):
        """입력 리스트 중복 제거 확인"""
        # 동일한 ID를 여러 번 보냄
        data = {"genre_ids": [self.genre1.id, self.genre1.id, self.genre2.id]}
        serializer = UserPreferenceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # 결과는 중복이 제거되어야 함
        self.assertEqual(len(serializer.validated_data["genre_ids"]), 2)


class PreferenceServiceTest(TestCase):
    """
    PreferenceService 비즈니스 로직 테스트
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
        create_user_preferences(self.user, genre_ids)

        self.assertEqual(Preference.objects.filter(user=self.user).count(), 2)

    def test_create_preferences_ignore_conflicts(self):
        """이미 존재하는 장르 등록 시도시 무시 (ignore_conflicts=True)"""
        # 1. 처음에 RPG 등록
        create_user_preferences(self.user, [self.genre1.id])
        self.assertEqual(Preference.objects.filter(user=self.user).count(), 1)

        # 2. RPG(중복) + FPS(신규) 등록 시도
        create_user_preferences(self.user, [self.genre1.id, self.genre2.id])

        # 3. 에러 없이 FPS만 추가되어 총 2개가 되어야 함
        self.assertEqual(Preference.objects.filter(user=self.user).count(), 2)

        rpg_pref = Preference.objects.get(user=self.user, genre=self.genre1)
        fps_pref = Preference.objects.get(user=self.user, genre=self.genre2)
        self.assertIsNotNone(rpg_pref)
        self.assertIsNotNone(fps_pref)


class PreferenceAPIViewTest(TestCase):
    """
    PreferenceAPIView 통합 테스트
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
        self.genre1 = Genre.objects.create(Genre="RPG", Genre_ko="모험")
        self.genre2 = Genre.objects.create(Genre="FPS", Genre_ko="총")

    def test_create_preference_unauthorized(self):
        """로그인하지 않은 상태로 요청 시 401 에러"""
        data = {"genre_ids": [self.genre1.id]}
        response = self.client.post(self.url, data, format="json")
        # 401확인
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED])

    def test_create_preference_success(self):
        """로그인 후 정상 등록 (201)"""
        self.client.force_authenticate(user=self.user)

        data = {"genre_ids": [self.genre1.id, self.genre2.id]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "저장 완료")

        # DB 확인
        self.assertTrue(
            Preference.objects.filter(user=self.user, genre_id=self.genre1.id).exists()
        )
        self.assertTrue(
            Preference.objects.filter(user=self.user, genre_id=self.genre2.id).exists()
        )

    def test_create_preference_invalid_data(self):
        """잘못된 데이터 요청 (400)"""
        self.client.force_authenticate(user=self.user)

        # 존재하지 않는 장르 ID
        data = {"genre_ids": [9999]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
