import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.diary import Diary
from app.models.note import Note
from app.models.user import User
from app.schemas.diary import DiaryGenerateRequest, DiaryRead
from app.services.ai import (
    companion_text_fallbacks,
    derive_diary_title_summary,
    fallback_diary_generation,
    generate_diary,
    stream_axiang_observation,
    stream_daily_ritual,
    stream_diary_plain_body,
    synthesize_axiang_and_ritual_text,
)

router = APIRouter()


def _sse_payload(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


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
    axiang, ritual = synthesize_axiang_and_ritual_text(diary_date, notes)
    diary = db.scalar(select(Diary).where(Diary.user_id == current_user.id, Diary.diary_date == diary_date))
    if diary is None:
        diary = Diary(
            user_id=current_user.id,
            diary_date=diary_date,
            title=generated.title,
            summary=generated.summary,
            content=generated.content,
            axiang_observation=axiang,
            daily_ritual=ritual,
        )
        db.add(diary)
    else:
        diary.title = generated.title
        diary.summary = generated.summary
        diary.content = generated.content
        diary.axiang_observation = axiang
        diary.daily_ritual = ritual
    db.commit()
    db.refresh(diary)
    return diary


@router.post("/generate/stream")
async def generate_diary_stream(
    payload: DiaryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """SSE：先写入占位日记拿到 id，再流式输出正文，结束后生成标题与摘要并落库。"""
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

    diary = db.scalar(select(Diary).where(Diary.user_id == current_user.id, Diary.diary_date == diary_date))
    if diary is None:
        diary = Diary(user_id=current_user.id, diary_date=diary_date, title="新日记", summary="", content="")
        db.add(diary)
    else:
        diary.title = "新日记"
        diary.summary = ""
        diary.content = ""
        diary.axiang_observation = ""
        diary.daily_ritual = ""
    db.commit()
    db.refresh(diary)

    async def event_gen():
        try:
            yield _sse_payload({"type": "meta", "diary_id": diary.id, "diary_date": diary.diary_date.isoformat()})
            parts: list[str] = []
            async for piece in stream_diary_plain_body(diary_date, notes):
                parts.append(piece)
                yield _sse_payload({"type": "chunk", "text": piece})
            full = "".join(parts)
            title, summary = derive_diary_title_summary(full, diary_date, notes)
            diary.content = full
            diary.title = title
            diary.summary = summary
            db.commit()

            yield _sse_payload({"type": "phase", "phase": "axiang"})
            ax_parts: list[str] = []
            try:
                async for piece in stream_axiang_observation(diary_date, notes):
                    ax_parts.append(piece)
                    yield _sse_payload({"type": "chunk_axiang", "text": piece})
                diary.axiang_observation = "".join(ax_parts)
            except Exception:  # noqa: BLE001
                fb_ax, _ = companion_text_fallbacks(diary_date, notes)
                diary.axiang_observation = fb_ax
                yield _sse_payload({"type": "chunk_axiang", "text": fb_ax})
            db.commit()

            yield _sse_payload({"type": "phase", "phase": "ritual"})
            ri_parts: list[str] = []
            try:
                async for piece in stream_daily_ritual(diary_date, notes):
                    ri_parts.append(piece)
                    yield _sse_payload({"type": "chunk_ritual", "text": piece})
                diary.daily_ritual = "".join(ri_parts)
            except Exception:  # noqa: BLE001
                _, fb_ri = companion_text_fallbacks(diary_date, notes)
                diary.daily_ritual = fb_ri
                yield _sse_payload({"type": "chunk_ritual", "text": fb_ri})
            db.commit()

            yield _sse_payload({"type": "done"})
        except Exception as e:  # noqa: BLE001
            fb = fallback_diary_generation(diary_date, notes)
            fb_ax, fb_ri = companion_text_fallbacks(diary_date, notes)
            diary.content = fb.content
            diary.title = fb.title
            diary.summary = fb.summary
            diary.axiang_observation = fb_ax
            diary.daily_ritual = fb_ri
            db.commit()
            yield _sse_payload({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
