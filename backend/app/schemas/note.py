from datetime import date, datetime
from pydantic import BaseModel, Field
from app.schemas.common import GridTag


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    record_date: date | None = None


class NoteRead(BaseModel):
    id: int
    content: str
    record_date: date
    energy_score: int = Field(ge=1, le=5)
    grid_tag: GridTag
    ai_comment: str
    ai_ready: bool
    created_at: datetime

    model_config = {'from_attributes': True}
