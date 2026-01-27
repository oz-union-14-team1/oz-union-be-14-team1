from apps.game.models.game import Game
from apps.game.models.genre import Genre
from apps.game.models.game_genre import GameGenre
from apps.game.models.tag import Tag
from apps.game.models.game_tag import GameTag
from apps.game.models.platform import Platform
from apps.game.models.game_platform import GamePlatform
from apps.game.models.game_img import GameImg

__all__ = [
    "Game",
    "Genre",
    "GameGenre",
    "Tag",
    "GameTag",
    "Platform",
    "GamePlatform",
    "GameImg",
]
