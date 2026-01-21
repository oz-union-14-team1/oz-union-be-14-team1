from django.test import TestCase
from apps.user.constants.period import Period
from apps.user.constants.time import ONE_HOUR, ONE_MINUTE, ONE_DAY


class PeriodTestCase(TestCase):
    #  period 상수들 TTL 값이 올바르게 설정되어 있는지 검증하는 테스트
    def test_ttl_values(self):
        self.assertEqual(Period.HOURLY.ttl, ONE_HOUR)
        self.assertEqual(Period.MINUTE.ttl, ONE_MINUTE)
        self.assertEqual(Period.DAILY.ttl, ONE_DAY)
