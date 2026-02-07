from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache

from apps.user.models.user import User
from apps.ai.models import UserTendency
from apps.ai.services.user_tendency_service import UserTendencyService


class UserTendencyServiceTest(TestCase):
    def setUp(self):
        # 1. genai.Client를 setUp 단계에서 미리 Mocking
        self.client_patcher = patch(
            "apps.ai.services.user_tendency_service.genai.Client"
        )
        self.mock_client_class = self.client_patcher.start()

        # 테스트가 끝나면 패치를 해제하도록 등록
        self.addCleanup(self.client_patcher.stop)

        # 2. 유저 생성
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )

        # 3. 서비스 생성 (위에서 만든 가짜 Client가 주입됨)
        self.service = UserTendencyService()

        # 캐시 초기화
        cache.clear()

    def test_get_or_create_tendency_returns_completed(self):
        """
        DB에 이미 성향 데이터가 있다면, 분석 요청 없이 결과를 반환해야 한다.
        """
        UserTendency.objects.create(user=self.user, tendency="전략가")

        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["tendency"], "전략가")

    @patch("apps.ai.tasks.user_tendency.run_user_tendency_analysis")
    def test_get_or_create_tendency_returns_processing_if_cached(self, mock_task):
        """
        DB엔 없지만 현재 분석 중(캐시 존재)이라면, 작업을 중복 실행하지 않는다.
        """
        cache_key = f"tendency_analysis_lock_{self.user.id}"
        cache.set(cache_key, "processing", timeout=10)

        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "processing")
        mock_task.delay.assert_not_called()

    @patch("apps.ai.tasks.user_tendency.run_user_tendency_analysis")
    def test_get_or_create_tendency_starts_new_analysis(self, mock_task):
        """
        데이터도 없고 분석 중도 아니라면, 새로운 분석 태스크를 실행해야 한다.
        """
        result = self.service.get_or_create_tendency(self.user)

        self.assertEqual(result["status"], "processing")
        mock_task.delay.assert_called_once_with(self.user.id)

        cache_key = f"tendency_analysis_lock_{self.user.id}"
        self.assertEqual(cache.get(cache_key), "processing")

    @patch(
        "apps.preference.services.preference_list_service.get_user_total_preferences"
    )
    def test_analyze_and_save_success(self, mock_get_prefs):
        """
        [Case 4] 실제 분석 로직: 선호 데이터가 있으면 AI를 호출하고 DB에 저장한다.
        """
        # Given: 선호도 데이터 Mock 설정
        mock_genre = MagicMock()
        mock_genre.genre = "RPG"
        mock_tag = MagicMock()
        mock_tag.tag = "Story"

        mock_get_prefs.return_value = {"Genres": [mock_genre], "Tags": [mock_tag]}

        # AI 응답 설정 (setUp에서 만든 Mock Class의 인스턴스를 가져옴)
        mock_instance = self.mock_client_class.return_value

        # 실제 호출될 때 반환할 값 설정
        mock_response = MagicMock()
        mock_response.text = '{"tendency": "모험을 즐기는 영웅"}'
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

        # 프롬프트 내용 확인
        call_args = mock_instance.models.generate_content.call_args
        prompt_text = call_args.kwargs["contents"]
        self.assertIn("RPG", prompt_text)
        self.assertIn("Story", prompt_text)

    @patch(
        "apps.preference.services.preference_list_service.get_user_total_preferences"
    )
    def test_analyze_and_save_default_if_no_preferences(self, mock_get_prefs):
        """
        [Case 5] 선호 데이터가 하나도 없으면 AI 호출 없이 기본값을 저장한다.
        """
        # Given
        mock_get_prefs.return_value = {"Genres": [], "Tags": []}

        # When
        result = self.service.analyze_and_save(self.user)

        # Then
        self.assertEqual(result["tendency"], None)
        self.assertTrue(
            UserTendency.objects.filter(
                user=self.user, tendency=None
            ).exists()
        )

        # AI 호출이 없어야 함
        mock_instance = self.mock_client_class.return_value
        mock_instance.models.generate_content.assert_not_called()
