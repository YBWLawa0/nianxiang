from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import SessionLocal, get_db
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteRead
from app.services.ai import evaluate_note

router = APIRouter()


def _fill_note_ai(note_id: int, content: str) -> None:
    evaluation = evaluate_note(content)
    db = SessionLocal()
    try:
        note = db.get(Note, note_id)
        if note is None:
            return
        note.energy_score = evaluation.energy_score
        note.grid_tag = evaluation.grid_tag.value
        note.ai_comment = evaluation.ai_comment
        db.commit()
    finally:
        db.close()


@router.post("", response_model=NoteRead)
def create_note(
    payload: NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Note:
    record_date = payload.record_date or date.today()
    note = Note(
        user_id=current_user.id,
        content=payload.content,
        record_date=record_date,
        energy_score=3,
        grid_tag='其他',
        ai_comment='',
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    background_tasks.add_task(_fill_note_ai, note.id, payload.content)
    return note


@router.get("", response_model=list[NoteRead])
def list_notes(date: date | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Note]:
    query = select(Note).where(Note.user_id == current_user.id)
    if date is not None:
        query = query.where(Note.record_date == date)
    query = query.order_by(Note.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Note:
    note = db.get(Note, note_id)
    if note is None or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="随笔不存在")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    note = db.get(Note, note_id)
    if note is None or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="随笔不存在")
    db.delete(note)
    db.commit()
