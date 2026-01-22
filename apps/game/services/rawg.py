import requests
from config.settings import RAWG_API_KEY

RAWG_URL = "https://api.rawg.io/api/games"


# rawg에서 한 번에 40개 까지만 제공 25*40=1000
def fetch_games(page: int = 25, page_size: int = 40):
    response = requests.get(
        RAWG_URL,
        params={
            "key": RAWG_API_KEY,
            "page": page,
            "page_size": page_size,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["results"]
