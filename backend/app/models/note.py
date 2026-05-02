from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Note(Base):
    __tablename__ = 'notes'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    record_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    energy_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    grid_tag: Mapped[str] = mapped_column(String(32), nullable=False, default='其他')
    ai_comment: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship('User', back_populates='notes')

    @property
    def ai_ready(self) -> bool:
        return bool((self.ai_comment or '').strip())
