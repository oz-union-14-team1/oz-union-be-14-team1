import requests
from django.conf import settings

RAWG_BASE_URL = "https://api.rawg.io/api"
PAGE_SIZE = 40  # rawg api에서 제공하는 최대 페이지 사이즈가 40
MAX_PAGE = 1  # 40개만 긁어오기


class RawgClient:
    def fetch_games(self):
        games = []

        for page in range(1, MAX_PAGE + 1):
            response = requests.get(
                f"{RAWG_BASE_URL}/games",
                params={
                    "key": settings.RAWG_API_KEY,
                    "page": page,
                    "page_size": PAGE_SIZE,
                },
                timeout=10,
            )
            response.raise_for_status()  # 오류나면 종료

            data = response.json()
            games.extend(data.get("results", []))

            if not data.get("next"):
                break

        return games

    def fetch_game_detail(self, game_id):
        response = requests.get(
            f"{RAWG_BASE_URL}/games/{game_id}",
            params={"key": settings.RAWG_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def fetch_game_screenshots(self, game_id):
        response = requests.get(
            f"{RAWG_BASE_URL}/games/{game_id}/screenshots",
            params={"key": settings.RAWG_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
