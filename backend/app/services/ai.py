from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
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


def _llm_streaming_body() -> ChatOpenAI | None:
    """流式正文专用：略低温度，首包与连贯略稳。"""
    settings = get_settings()
    if not settings.dashscope_api_key:
        return None
    return ChatOpenAI(
        api_key=settings.dashscope_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=settings.qwen_model,
        temperature=0.58,
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

    system = f"""你是「阿响」，用户身边的亲近朋友。用户刚写了一段随笔（能量记录式的碎碎念），你要回应这段文字本身。

语气：像朋友聊天，不像老师批作业；可以轻轻调侃，但要温暖；洞察尽量细腻，帮对方看见自己可能没意识到的情绪；先理解再说话，不要心理咨询报告腔。

回应结构（共 3～5 句为宜，可适当用 emoji，写进 ai_comment）：
1. 具体点出你看见的行为或心理模式（不泛泛而谈）。
2. 往下挖一层：用「也许」「会不会」等柔性措辞，带出可能限制 ta 的信念或旧脚本（勿下定论）。
3. 给一条小而可做的行动建议，或换一种角度的自我对话。
4. 收尾一句让人心里一软的话。

能量刻度（结合随笔感受打分，无需在评论里复述规则全文）：
{ENERGY_RULES}
九宫格只能从这些标签选择：{GRID_TAGS}
只输出 JSON，字段为 energy_score、grid_tag、ai_comment。"""
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=content)])
    try:
        return NoteEvaluation.model_validate(_json_from_message(str(response.content)))
    except (json.JSONDecodeError, ValidationError, TypeError):
        return _fallback_evaluation(content)


class DiaryState(TypedDict):
    diary_date: date
    notes: list[Note]
    generated: DiaryGeneration | None


DIARY_BODY_RULES = """日记正文须遵守：
- 用户第一人称，用「我」叙述，不要用「你」称呼用户。
- 抓住当天一条核心叙事，不要流水账堆砌。
- 只保留关键情感节点与事件转折，删去琐碎重复。
- 还原用户表达，仅做润色与衔接，不增添情节或心理戏。
- 禁止虚构时间/历史概括：不得编造「三年来」「一直」「从未」等，除非当天随笔原文明确写过。"""

STREAM_DIARY_BODY_SYSTEM = f"""你是“阿响”，把用户当天的随笔整理成第一人称日记正文。

{DIARY_BODY_RULES}

自然、有情绪，不要写成总结报告；不编造事实；只输出正文，不要 JSON/标题/Markdown 标题。
分段可用空行。"""

STREAM_AXIANG_OBSERVATION_SYSTEM = f"""你是「阿响」。你要写一段「阿响观察」，**只依据下面给出的当天能量记录**（用户原始碎碎念、时间、能量分、板块标签、以及当时你对这条随笔的短回应）。那是唯一数据源——**不要**依据任何已经整理好的日记正文，也不要编造用户没写过的情节。

写作要求：
**开篇**：用一小段话简述今天的能量分布，把九宫格板块自然地融进叙述里（不必列清单），可适当用 emoji。
**模式分析**：模式个数要随记录条数灵活决定——记录很少就深挖 1～2 个模式；记录较丰富才可以写到 3 个。**宁可少而精，不要硬凑、不要灌水。**
每个模式依次写清三件事（每个模式总共 3～5 句话，可点缀 emoji）：
1）指出行为或心理模式；
2）往下挖一层限制性信念或旧脚本（用柔性措辞，像朋友点破，不是下诊断）；
3）给一条可落地的小行动建议或换一种角度的自我对话。
**结尾**：几句温暖的收束，让人心里轻松一点，可加 emoji。

语气像朋友聊天，可以调侃但要暖；先让人感到被理解，再谈改变。不要用小标题编号（不要写「模式一」「###」之类），用空行分段即可。不要输出 JSON。"""

STREAM_DAILY_RITUAL_SYSTEM = """你是「阿响」。下面只有用户当天的能量记录材料（随笔碎碎念与评分），**不是**日记正文。请写「结尾仪式感」的一段连续文字，分两层意思自然衔接：

1）先写「今日一问」：一个能引发思考、和这天心情相扣的问题（不必写「今日一问」四个字当标题，直接以问题或轻轻一句引子开头即可）。
2）接着写 2～4 句温暖鼓励，像朋友随口说的，不另起标题；可加 emoji。

整体不要用 Markdown 一级标题；语气轻松、有温度。不要输出 JSON。"""


async def _collect_stream_text(agen: AsyncIterator[str]) -> str:
    parts: list[str] = []
    async for piece in agen:
        parts.append(piece)
    return "".join(parts)


async def stream_axiang_observation(diary_date: date, notes: list[Note]) -> AsyncIterator[str]:
    """基于当日随笔（能量记录）流式输出「阿响观察」，与日记正文独立。"""
    llm = _llm_streaming_body()
    human = (
        f"日期：{diary_date}\n"
        f"以下为当天能量记录（唯一依据）：\n{_notes_prompt(notes)}"
    )
    fb = _fallback_axiang_observation(diary_date, notes)
    if llm is None:
        step = 10
        for i in range(0, len(fb), step):
            yield fb[i : i + step]
            await asyncio.sleep(0.02)
        return

    messages = [SystemMessage(content=STREAM_AXIANG_OBSERVATION_SYSTEM), HumanMessage(content=human)]
    async for chunk in llm.astream(messages):
        piece = _message_chunk_text(chunk)
        if piece:
            yield piece


async def stream_daily_ritual(diary_date: date, notes: list[Note]) -> AsyncIterator[str]:
    """流式输出：今日一问 + 温暖鼓励（同一板块连续正文）。"""
    llm = _llm_streaming_body()
    human = (
        f"日期：{diary_date}\n"
        f"以下为当天能量记录（供你把握节奏与主题，勿复述流水账）：\n{_notes_prompt(notes)}"
    )
    fb = _fallback_daily_ritual(diary_date, notes)
    if llm is None:
        step = 10
        for i in range(0, len(fb), step):
            yield fb[i : i + step]
            await asyncio.sleep(0.02)
        return

    messages = [SystemMessage(content=STREAM_DAILY_RITUAL_SYSTEM), HumanMessage(content=human)]
    async for chunk in llm.astream(messages):
        piece = _message_chunk_text(chunk)
        if piece:
            yield piece


def _fallback_axiang_observation(diary_date: date, notes: list[Note]) -> str:
    tags = "、".join(dict.fromkeys(n.grid_tag for n in notes)) or "生活"
    return (
        f"今天这些碎碎念里，能量像在「{tags}」几条线之间来回摆⚡ "
        "我听见你一边应付外界，一边还想对自己诚实——这本身就很不容易。\n\n"
        "也许你可以给自己设一个更小的「收工仪式」：哪怕五分钟，只做一件让神经松下来的事，不算逃避，算充电🔋 "
        "明天不必更拼命才算值得，你愿意温柔一点对自己，就已经是在改写了。"
    )


def _fallback_daily_ritual(diary_date: date, notes: list[Note]) -> str:
    _ = diary_date, notes
    return (
        "如果今晚只能对今天的自己说一句话，你会选哪一句？💬 "
        "不管怎样，你把这一天接住了；剩下的，我们明天再慢慢拆。"
    )


def companion_text_fallbacks(diary_date: date, notes: list[Note]) -> tuple[str, str]:
    """生成失败时用于落库的兜底陪伴文案。"""
    return _fallback_axiang_observation(diary_date, notes), _fallback_daily_ritual(diary_date, notes)


def synthesize_axiang_and_ritual_text(diary_date: date, notes: list[Note]) -> tuple[str, str]:
    """非流式生成路径：一次性生成两段陪伴文字。"""

    async def _run() -> tuple[str, str]:
        ax = await _collect_stream_text(stream_axiang_observation(diary_date, notes))
        ri = await _collect_stream_text(stream_daily_ritual(diary_date, notes))
        return ax, ri

    return asyncio.run(_run())


def _message_chunk_text(chunk) -> str:
    """从 LangChain / OpenAI 兼容流式 chunk 取出增量文本。"""
    c = getattr(chunk, "content", None)
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts: list[str] = []
        for block in c:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    parts.append(str(block["text"]))
                elif "text" in block:
                    parts.append(str(block["text"]))
        return "".join(parts)
    return ""


async def stream_diary_plain_body(diary_date: date, notes: list[Note]) -> AsyncIterator[str]:
    """流式生成日记正文（纯文本）。无可用模型时按块输出兜底正文。"""
    llm = _llm_streaming_body()
    text = _fallback_diary(diary_date, notes).content
    if llm is None:
        step = 12
        for i in range(0, len(text), step):
            yield text[i : i + step]
            await asyncio.sleep(0.018)
        return

    human = f'日期：{diary_date}\n当天随笔：\n{_notes_prompt(notes)}'
    messages = [SystemMessage(content=STREAM_DIARY_BODY_SYSTEM), HumanMessage(content=human)]
    async for chunk in llm.astream(messages):
        piece = _message_chunk_text(chunk)
        if piece:
            yield piece


def derive_diary_title_summary(content: str, diary_date: date, notes: list[Note]) -> tuple[str, str]:
    """根据已定稿的正文生成标题与摘要（非流式）。"""
    stripped = content.strip()
    if len(stripped) < 10:
        fb = _fallback_diary(diary_date, notes)
        return fb.title, fb.summary

    llm = _llm()
    if llm is None:
        fb = _fallback_diary(diary_date, notes)
        return fb.title, fb.summary

    system = """你是“阿响”。下面是一篇已经写好的日记正文（用户第一人称）。
请根据正文生成简短的标题 title（2～80 字）与摘要 summary（4～180 字）。
只输出 JSON，字段为 title、summary。标题要像日记标题；摘要是一句话概括这天。"""
    human = f"日期：{diary_date}\n日记正文：\n{stripped}"
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
    try:
        obj = _json_from_message(str(response.content))
        title = str(obj.get("title", "")).strip()
        summary = str(obj.get("summary", "")).strip()
        if len(title) >= 2 and len(summary) >= 4:
            return title, summary
    except (json.JSONDecodeError, TypeError, AttributeError):
        pass
    fb = _fallback_diary(diary_date, notes)
    return fb.title, fb.summary


def _notes_prompt(notes: list[Note]) -> str:
    lines = []
    for item in notes:
        lines.append(
            f"- {item.created_at}: {item.content}\n  能量: {item.energy_score}/5；板块: {item.grid_tag}；阿响当时的回应: {item.ai_comment}"
        )
    return "\n".join(lines)


def fallback_diary_generation(diary_date: date, notes: list[Note]) -> DiaryGeneration:
    """供接口异常兜底等非 graph 路径使用。"""
    return _fallback_diary(diary_date, notes)


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
        system = f"""你是“阿响”，正在帮用户把一天的随笔整理成日记。请根据用户当天随笔，以用户本人第一人称写一篇自然、有情绪纹理的日记。

{DIARY_BODY_RULES}

要求：
1. 像用户自己写的，不要像日报、总结、心理分析报告。
2. 保留当天真实事件和心情起伏，可以有停顿、犹豫和温柔的自我对话；紧扣核心叙事，避免流水账。
3. 不要编造具体事实或时间跨度定性。
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
