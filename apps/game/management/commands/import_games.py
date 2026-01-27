from django.core.management.base import BaseCommand
from apps.game.services.importer import GameImportService


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('게임 데이터 가져오기 시작...')

        service = GameImportService()
        count = service.import_games()

        self.stdout.write(
            self.style.SUCCESS(f'성공! {count}개의 게임이 추가되었습니다.')
        )
