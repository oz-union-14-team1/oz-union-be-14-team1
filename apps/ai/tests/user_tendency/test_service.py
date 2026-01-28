from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache

from apps.user.models.user import User
from apps.ai.models import UserTendency
from apps.ai.services.user_tendency_service import UserTendencyService


class UserTendencyServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )

        self.service = UserTendencyService()
        cache.clear()

    def test_get_or_create_tendency_returns_completed(self):
        UserTendency.objects.create(user=self.user, tendency="전략가")
        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["tendency"], "전략가")

    @patch("apps.ai.tasks.user_tendency.run_user_tendency_analysis")
    def test_get_or_create_tendency_returns_processing_if_cached(self, mock_task):
        cache_key = f"debounce_tendency_analysis_{self.user.id}"
        cache.set(cache_key, "processing", timeout=10)

        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "processing")
        mock_task.delay.assert_not_called()

    @patch("apps.ai.tasks.user_tendency.run_user_tendency_analysis")
    def test_get_or_create_tendency_starts_new_analysis(self, mock_task):
        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "processing")
        mock_task.delay.assert_called_once_with(self.user.id)

        cache_key = f"debounce_tendency_analysis_{self.user.id}"
        self.assertEqual(cache.get(cache_key), "processing")

    @patch("apps.ai.services.user_tendency_service.genai.Client")
    @patch(
        "apps.preference.services.preference_list_service.get_user_total_preferences"
    )
    def test_analyze_and_save_success(self, mock_get_prefs, mock_genai_client):
        self.service = UserTendencyService()

        # Given
        mock_genre = MagicMock()
        mock_genre.genre = "RPG"
        mock_tag = MagicMock()
        mock_tag.tag = "Story"

        mock_get_prefs.return_value = {"Genres": [mock_genre], "Tags": [mock_tag]}

        mock_response = MagicMock()
        mock_response.text = '{"tendency": "모험을 즐기는 영웅"}'

        mock_instance = mock_genai_client.return_value
        mock_instance.models.generate_content.return_value = mock_response

        # When
        result = self.service.analyze_and_save(self.user)

        # Then
        self.assertEqual(result["tendency"], "모험을 즐기는 영웅")
        self.assertTrue(
            UserTendency.objects.filter(
                user=self.user, tendency="모험을 즐기는 영웅"
            ).exists()
        )

        call_args = mock_instance.models.generate_content.call_args
        prompt_text = call_args.kwargs["contents"]
        self.assertIn("RPG", prompt_text)
        self.assertIn("Story", prompt_text)

    @patch("apps.ai.services.user_tendency_service.genai.Client")
    @patch(
        "apps.preference.services.preference_list_service.get_user_total_preferences"
    )
    def test_analyze_and_save_default_if_no_preferences(
        self, mock_get_prefs, mock_genai_client
    ):
        self.service = UserTendencyService()

        # Given
        mock_get_prefs.return_value = {"Genres": [], "Tags": []}

        # When
        result = self.service.analyze_and_save(self.user)

        # Then
        self.assertEqual(result["tendency"], "아직 모르는 게이머")
        self.assertTrue(
            UserTendency.objects.filter(
                user=self.user, tendency="아직 모르는 게이머"
            ).exists()
        )

        mock_instance = mock_genai_client.return_value
        mock_instance.models.generate_content.assert_not_called()
