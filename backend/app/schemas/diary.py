from datetime import date, datetime
from pydantic import BaseModel


class DiaryGenerateRequest(BaseModel):
    diary_date: date | None = None


class DiaryRead(BaseModel):
    id: int
    diary_date: date
    title: str
    summary: str
    content: str
    axiang_observation: str = ''
    daily_ritual: str = ''
    created_at: datetime

    model_config = {'from_attributes': True}
