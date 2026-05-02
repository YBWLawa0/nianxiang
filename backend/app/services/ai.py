from __future__ import annotations

import json
from datetime import date
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings
from app.models.note import Note
from app.schemas.common import GridTag

ENERGY_RULES = """1分（极度耗电）：被迫感、崩溃、环境极度压抑
2分（轻微失血）：平庸杂事、低效社交、不得不做的消耗
3分（平稳波动）：中性陈述、日常惯性、不咸不淡
4分（轻微回血）：正向反馈、小确幸、审美享受、放松
5分（满电心流）：深度投入、突破性进展、灵性瞬间"""

GRID_TAGS = "、".join(tag.value for tag in GridTag)


class NoteEvaluation(BaseModel):
    energy_score: int = Field(ge=1, le=5)
    grid_tag: GridTag
    ai_comment: str = Field(min_length=4, max_length=500)


class DiaryGeneration(BaseModel):
    title: str = Field(min_length=2, max_length=80)
    summary: str = Field(min_length=4, max_length=180)
    content: str = Field(min_length=20, max_length=4000)


def _llm() -> ChatOpenAI | None:
    settings = get_settings()
    if not settings.dashscope_api_key:
        return None
    return ChatOpenAI(
        api_key=settings.dashscope_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=settings.qwen_model,
        temperature=0.75,
    )


def _json_from_message(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json\n", "", 1).replace("JSON\n", "", 1)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        text = text[start : end + 1]
    return json.loads(text)


def _fallback_evaluation(content: str) -> NoteEvaluation:
    positive = ["开心", "舒服", "喜欢", "完成", "进展", "放松", "好看", "顺利", "期待", "安静"]
    negative = ["累", "崩溃", "烦", "压抑", "被迫", "焦虑", "失眠", "难受", "讨厌", "麻木"]
    score = 3 + min(2, sum(word in content for word in positive)) - min(2, sum(word in content for word in negative))
    score = max(1, min(5, score))
    tag = GridTag.other
    keyword_tags = [
        (GridTag.work, ["工作", "项目", "会议", "同事", "老板", "事业"]),
        (GridTag.health, ["身体", "睡", "病", "运动", "疼", "健康"]),
        (GridTag.emotion, ["喜欢", "爱", "关系", "孤独", "想念", "亲密"]),
        (GridTag.finance, ["钱", "消费", "工资", "理财", "账单"]),
        (GridTag.growth, ["学习", "读书", "课程", "成长", "复盘"]),
        (GridTag.leisure, ["电影", "游戏", "散步", "咖啡", "音乐", "休息"]),
        (GridTag.family, ["家", "爸", "妈", "孩子", "伴侣"]),
        (GridTag.social, ["朋友", "聚会", "聊天", "社交"]),
    ]
    for candidate, words in keyword_tags:
        if any(word in content for word in words):
            tag = candidate
            break
    return NoteEvaluation(
        energy_score=score,
        grid_tag=tag,
        ai_comment="我听见你把这一刻认真放下来了。它不需要马上被解决，也可以先被理解：这段经历更像是在提醒你，留一点空间给自己的真实感受。",
    )


def evaluate_note(content: str) -> NoteEvaluation:
    llm = _llm()
    if llm is None:
        return _fallback_evaluation(content)

    system = f"""你是“念想”，用户的数字分身和亲近朋友。请温柔、具体、不说教地回应用户随笔。
能量刻度规则：
{ENERGY_RULES}
九宫格只能从这些标签选择：{GRID_TAGS}
只输出 JSON，字段为 energy_score、grid_tag、ai_comment。ai_comment 要像朋友对本人说话，亲切、有共情，不要心理咨询腔。"""
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=content)])
    try:
        return NoteEvaluation.model_validate(_json_from_message(str(response.content)))
    except (json.JSONDecodeError, ValidationError, TypeError):
        return _fallback_evaluation(content)


class DiaryState(TypedDict):
    diary_date: date
    notes: list[Note]
    generated: DiaryGeneration | None


def _notes_prompt(notes: list[Note]) -> str:
    lines = []
    for item in notes:
        lines.append(
            f"- {item.created_at}: {item.content}\n  能量: {item.energy_score}/5；板块: {item.grid_tag}；AI当时的回应: {item.ai_comment}"
        )
    return "\n".join(lines)


def _fallback_diary(diary_date: date, notes: list[Note]) -> DiaryGeneration:
    summary = "、".join(dict.fromkeys(note.grid_tag for note in notes)) or "今天的片段"
    body = ["今天我留下了几段很真实的念头。"]
    for note in notes:
        body.append(f"我记得自己写下：“{note.content}”")
    body.append("这些话放在一起，好像让我更确定：我不是非要把每一件事都处理得漂亮，能诚实地看见自己，就已经是在往前走了。")
    return DiaryGeneration(
        title=f"{diary_date:%m月%d日}，我和自己待了一会儿",
        summary=f"关于{summary}的一天。",
        content="\n\n".join(body),
    )


def generate_diary(diary_date: date, notes: list[Note]) -> DiaryGeneration:
    llm = _llm()
    if llm is None:
        return _fallback_diary(diary_date, notes)

    def write_node(state: DiaryState) -> DiaryState:
        system = """你是“念想”的日记写作者。请根据用户当天随笔，以用户本人第一人称写一篇自然、有情绪纹理的日记。
要求：
1. 像用户自己写的，不要像日报、总结、心理分析报告。
2. 保留当天真实事件和心情起伏，可以有停顿、犹豫和温柔的自我对话。
3. 不要编造具体事实。
4. 输出 JSON，字段为 title、summary、content。"""
        human = f'日期：{state["diary_date"]}\n当天随笔：\n{_notes_prompt(state["notes"])}'
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        try:
            generated = DiaryGeneration.model_validate(_json_from_message(str(response.content)))
        except (json.JSONDecodeError, ValidationError, TypeError):
            generated = _fallback_diary(state["diary_date"], state["notes"])
        return {**state, "generated": generated}

    graph = StateGraph(DiaryState)
    graph.add_node("write_diary", write_node)
    graph.set_entry_point("write_diary")
    graph.add_edge("write_diary", END)
    app = graph.compile()
    result = app.invoke({"diary_date": diary_date, "notes": notes, "generated": None})
    return result["generated"] or _fallback_diary(diary_date, notes)
