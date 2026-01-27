from pydantic import BaseModel, Field

# 기존 GameSummary 아래에 추가
class UserTendency(BaseModel):
    """
    유저 성향 분석 결과 구조
    """
    tendency: str = Field(description="유저의 성향을 나타내는 10자 이내의 짧은 문구")