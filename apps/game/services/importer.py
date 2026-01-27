from datetime import datetime
import time
from apps.game.models.game import Game
from apps.game.models.genre import Genre
from apps.game.models.game_genre import GameGenre
from apps.game.models.tag import Tag
from apps.game.models.game_tag import GameTag
from apps.game.services.rawg import RawgClient


class GameImportService:
    def import_games(self):
        raw_games = RawgClient().fetch_games()
        client = RawgClient()
        games = []
        game_genres_data = []
        game_tags_data = []

        for g in raw_games:
            if Game.objects.filter(name=g["name"]).exists():
                continue

            try:
                detail = client.fetch_game_detail(g["id"])

                developer = "Unknown"
                if detail.get("developers") and len(detail["developers"]) > 0:
                    developer = detail["developers"][0]["name"]

                publisher = "Unknown"
                if detail.get("publishers") and len(detail["publishers"]) > 0:
                    publisher = detail["publishers"][0]["name"]

                intro = detail.get("description", "") or ""

                genres_info = detail.get("genres", [])

                tags_info = detail.get("tags", [])

                time.sleep(0.3)

            except Exception as e:
                print(f"오류 발생: {g['name']} - {e}")
                developer = "Unknown"
                publisher = "Unknown"
                intro = ""
                genres_info = []
                tags_info = []

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
                    publisher=publisher,
                )
            )

            game_genres_data.append({"game_name": g["name"], "genres": genres_info})

            game_tags_data.append({"game_name": g["name"], "tags": tags_info})

        Game.objects.bulk_create(games)
        self.import_genres(game_genres_data)
        self.import_tags(game_tags_data)

        print(f"\n{len(games)}개의 새로운 게임이 추가되었습니다.")
        return len(games)

    def import_genres(self, game_genres_data):
        game_genre_relation = []

        for data in game_genres_data:
            try:
                game = Game.objects.get(name=data["game_name"])
            except Game.DoesNotExist:
                continue

            for genre_info in data["genres"]:
                genre, created = Genre.objects.get_or_create(
                    slug=genre_info["slug"],
                    genre=genre_info["name"],
                )

                game_genre_relation.append(GameGenre(game=game, genre=genre))

        GameGenre.objects.bulk_create(game_genre_relation, ignore_conflicts=True)

    def import_tags(self, game_tags_data):
        game_tag_relation = []

        for data in game_tags_data:
            try:
                game = Game.objects.get(name=data["game_name"])
            except Game.DoesNotExist:
                continue

            for tag_info in data["tags"]:
                tag, created = Tag.objects.get_or_create(
                    slug=tag_info["slug"],
                    tag=tag_info["name"],
                )

                game_tag_relation.append(GameTag(game=game, tag=tag))

        GameTag.objects.bulk_create(game_tag_relation, ignore_conflicts=True)
