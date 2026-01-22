from datetime import datetime

from apps.game.models.game import Game
from apps.game.services.rawg import RawgClient


class GameImportService:
    def import_games(self):
        raw_games = RawgClient().fetch_games()
        games = []

        for g in raw_games:
            Game(
                name=g["name"],
                intro=g.get("description_raw", ""),
                released_at=(
                    datetime.strptime(g["released"], "%Y-%m-%d")
                    if g.get("released")
                    else None
                ),
                developer=(
                    g["developers"][0]["name"]
                    if g.get("developers")
                    else "Unknown"
                )
            )

        Game.objects.bulk_create(games)
        return len(games)
