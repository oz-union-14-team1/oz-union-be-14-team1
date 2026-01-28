from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.utils import timezone

from apps.user.models.user import User
from apps.game.models.game import Game
from apps.ai.exceptions.ai_exceptions import AiGenerationFailed


class GameReviewSummaryAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test1234",
            nickname="test_user",
            phone_number="010-0000-0000",
        )
        self.game = Game.objects.create(
            name="Test Game",
            intro="Intro",
            released_at=timezone.now(),
            developer="developer",
            avg_score=5.0,
        )
        # URL 이름은 urls.py에 정의된 name과 일치해야 함
        self.url = reverse("game_summary", kwargs={"game_id": self.game.id})

    @patch("apps.ai.views.review_summary_view.ReviewSummaryService")
    def test_api_success_200(self, mock_service_class):
        """
        정상적인 요청 시 200 OK와 JSON 데이터를 반환하는지 테스트
        """
        # Given: Service가 정상적인 딕셔너리를 반환하도록 Mocking
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.get_summary.return_value = {
            "good_points": ["Good"],
            "bad_points": ["Bad"],
            "total_review": "Summary",
        }

        # When: API 엔드포인트에 GET 요청
        response = self.client.get(self.url)

        # Then: 200 상태코드와 반환된 데이터 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_review"], "Summary")

    def test_api_invalid_game_id_400(self):
        """
        존재하지 않는 게임 ID 요청 시 400 Bad Request 반환 테스트
        """
        # Given: 존재하지 않는 게임 ID로 URL 생성
        invalid_url = self.url.replace(str(self.game.id), "99999")

        # When: 잘못된 ID로 GET 요청
        response = self.client.get(invalid_url)

        # Then: 404 에러 반환 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.ai.views.review_summary_view.ReviewSummaryService")
    def test_api_service_error_503(self, mock_service_class):
        """
        서비스에서 AiGenerationFailed 발생 시 503 에러 반환 테스트
        """
        # Given: Service가 AiGenerationFailed 예외를 던지도록 설정
        mock_service_instance = mock_service_class.return_value
        mock_service_instance.get_summary.side_effect = AiGenerationFailed()

        # When: API 엔드포인트에 GET 요청
        response = self.client.get(self.url)

        # Then: 503 에러 반환 검증
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
