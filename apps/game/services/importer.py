# games/services/importer.py
from datetime import datetime
from apps.game.models.game import Game
from apps.game.services.rawg import fetch_games


def import_games(limit: int = 1000):
    total_pages = limit // 40
    created = 0

    for page in range(1, total_pages + 1):
        games = fetch_games(page, 40)

        for g in games:
            if not g.get("released"):
                continue

            developer = "Unknown"
            if g.get("developers"):
                developer = g["developers"][0]["name"]

            Game.objects.create(
                name=g["name"],
                intro=g.get("description_raw") or "No description",
                released_at=datetime.fromisoformat(g["released"]),
                developer=developer,
                avg_score=g.get("rating", 0),
            )

            created += 1
            if created >= limit:
                return created

    return created
