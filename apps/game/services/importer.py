from datetime import datetime
import time
from apps.game.models.game import Game
from apps.game.services.rawg import RawgClient


class GameImportService:
    def import_games(self):
        raw_games = RawgClient().fetch_games()
        client = RawgClient()
        games = []

        for g in raw_games:
            if Game.objects.filter(name=g["name"]).exists():
                continue

            try:
                detail = client.fetch_game_detail(g["id"])

                developer = "Unknown"
                if detail.get("developers") and len(detail["developers"]) > 0:
                    developer = detail["developers"][0]["name"]

                intro = detail.get("description", "") or ""

                # API 호출 제한 방지 (초당 3-4번 정도)
                time.sleep(0.3)

            except Exception as e:
                print(f"오류 발생: {g['name']} - {e}")
                developer = "Unknown"
                intro = ""

            released_at = None
            if g.get("released"):
                try:
                    released_at = datetime.strptime(g["released"], "%Y-%m-%d").date()
                except ValueError:
                    pass

            games.append(
                Game(
                    name=g["name"],
                    intro=intro[:500] if intro else "",
                    released_at=released_at,
                    developer=developer,
                )
            )

        Game.objects.bulk_create(games)
        print(f"\n완료! {len(games)}개의 새로운 게임이 추가되었습니다.")

        return len(games)
