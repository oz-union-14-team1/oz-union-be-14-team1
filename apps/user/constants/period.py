from enum import Enum

class Period(str, Enum):
    HOURLY = "hourly"
    MINUTE = "minute"
    DAILY = "daily"

    # 나중에 쓸 수도 있을거같아서 미리..
    @property
    def ttl(self):
        from .time import ONE_HOUR, ONE_MINUTE, ONE_DAY

        return {
            Period.HOURLY: ONE_HOUR,
            Period.MINUTE: ONE_MINUTE,
            Period.DAILY: ONE_DAY,
        }[self]