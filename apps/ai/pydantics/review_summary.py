from pydantic import BaseModel, Field


class GameSummary(BaseModel):
    """
    AI가 생성할 요약 결과의 구조
    """

    good_points: list[str] = Field(description="유저들이 칭찬하는 점")
    bad_points: list[str] = Field(description="유저들이 비판하는 점")
    total_review: str = Field(description="전체적인 총평")
