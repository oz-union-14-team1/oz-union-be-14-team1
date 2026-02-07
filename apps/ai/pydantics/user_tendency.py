from pydantic import BaseModel, Field
from typing import Optional

class UserTendency(BaseModel):
    """
    유저 성향 분석 결과 구조
    """

    tendency: Optional[str] = Field(None, description="유저의 성향을 나타내는 10자 이내의 짧은 문구")
