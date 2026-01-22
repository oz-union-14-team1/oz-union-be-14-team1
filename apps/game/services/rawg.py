import requests
from django.conf import settings

RAWG_BASE_URL = "https://api.rawg.io/api"
PAGE_SIZE = 40 #rawg api에서 제공하는 최대 페이지 사이즈가 40
MAX_PAGE = 25  # 25 * 40 = 1000 관리자만 사용할거니까 그냥 1000개 긁어옴

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
                timeout=5,
            )
            response.raise_for_status() #오류나면 종료

            data = response.json()
            games.extend(data.get("results", []))

        return games
