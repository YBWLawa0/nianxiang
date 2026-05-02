from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.diary import Diary
from app.models.note import Note
from app.models.user import User
from app.schemas.diary import DiaryGenerateRequest, DiaryRead
from app.services.ai import generate_diary

router = APIRouter()


@router.post("/generate", response_model=DiaryRead)
def generate_today_diary(payload: DiaryGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Diary:
    diary_date = payload.diary_date or date.today()
    notes = list(
        db.scalars(
            select(Note)
            .where(Note.user_id == current_user.id, Note.record_date == diary_date)
            .order_by(Note.created_at.asc())
        ).all()
    )
    if not notes:
        raise HTTPException(status_code=400, detail="今天还没有随笔，先记录一点再生成日记吧")

    generated = generate_diary(diary_date=diary_date, notes=notes)
    diary = db.scalar(select(Diary).where(Diary.user_id == current_user.id, Diary.diary_date == diary_date))
    if diary is None:
        diary = Diary(user_id=current_user.id, diary_date=diary_date, title=generated.title, summary=generated.summary, content=generated.content)
        db.add(diary)
    else:
        diary.title = generated.title
        diary.summary = generated.summary
        diary.content = generated.content
    db.commit()
    db.refresh(diary)
    return diary


@router.get("", response_model=list[DiaryRead])
def list_diaries(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Diary]:
    return list(
        db.scalars(
            select(Diary).where(Diary.user_id == current_user.id).order_by(Diary.diary_date.desc(), Diary.created_at.desc())
        ).all()
    )


@router.get("/{diary_id}", response_model=DiaryRead)
def get_diary(diary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Diary:
    diary = db.get(Diary, diary_id)
    if diary is None or diary.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="日记不存在")
    return diary
