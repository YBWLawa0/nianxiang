import api from './client'
import type { Diary } from '../types/domain'

const rawBase = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '')

export function generateDiary(date?: string) {
  return api.post<Diary>('/diaries/generate', { diary_date: date })
}

export type DiaryStreamMeta = { diary_id: number; diary_date: string }

export type DiaryStreamPhase = 'axiang' | 'ritual'

export async function generateDiaryStream(
  diaryDate: string | undefined,
  handlers: {
    onMeta: (m: DiaryStreamMeta) => void
    onChunk: (text: string) => void
    onPhase?: (phase: DiaryStreamPhase) => void
    onChunkAxiang?: (text: string) => void
    onChunkRitual?: (text: string) => void
    onDone: () => void
    onError: (message: string) => void
  },
  signal?: AbortSignal,
): Promise<void> {
  const token = localStorage.getItem('nianxiang_token')
  const res = await fetch(`${rawBase}/diaries/generate/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ diary_date: diaryDate }),
    signal,
  })

  if (res.status === 401) {
    localStorage.removeItem('nianxiang_token')
    handlers.onError('登录已过期')
    return
  }

  if (!res.ok) {
    let detail = '日记生成失败'
    try {
      const j = (await res.json()) as { detail?: unknown }
      const d = j.detail
      if (typeof d === 'string') detail = d
      else if (Array.isArray(d))
        detail = d.map((x: { msg?: string }) => x.msg ?? '').filter(Boolean).join('，') || detail
    } catch {
      /* ignore */
    }
    handlers.onError(detail)
    return
  }

  if (!res.body) {
    handlers.onError('无法读取响应')
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let terminal = false

  type Ev = {
    type: string
    text?: string
    message?: string
    diary_id?: number
    diary_date?: string
    phase?: string
  }

  function dispatch(obj: Ev) {
    if (obj.type === 'meta' && obj.diary_id != null && obj.diary_date != null) {
      handlers.onMeta({ diary_id: obj.diary_id, diary_date: obj.diary_date })
      return
    }
    if (obj.type === 'chunk') {
      handlers.onChunk(obj.text ?? '')
      return
    }
    if (obj.type === 'phase' && (obj.phase === 'axiang' || obj.phase === 'ritual')) {
      handlers.onPhase?.(obj.phase)
      return
    }
    if (obj.type === 'chunk_axiang') {
      handlers.onChunkAxiang?.(obj.text ?? '')
      return
    }
    if (obj.type === 'chunk_ritual') {
      handlers.onChunkRitual?.(obj.text ?? '')
      return
    }
    if (obj.type === 'done') {
      terminal = true
      handlers.onDone()
      return
    }
    if (obj.type === 'error') {
      terminal = true
      handlers.onError(obj.message ?? '生成出错')
    }
  }

  function parseBlocks(buf: string): { events: Ev[]; rest: string } {
    const events: Ev[] = []
    const parts = buf.split(/\n\n/)
    const rest = parts.pop() ?? ''
    for (const block of parts) {
      for (const line of block.split('\n')) {
        const t = line.trim()
        if (!t.startsWith('data:')) continue
        const raw = t.slice(5).trim()
        if (!raw) continue
        try {
          events.push(JSON.parse(raw) as Ev)
        } catch {
          /* skip malformed */
        }
      }
    }
    return { events, rest }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const { events, rest } = parseBlocks(buffer)
    buffer = rest
    for (const ev of events) dispatch(ev)
    if (terminal) break
  }

  if (!terminal && buffer.trim()) {
    const { events } = parseBlocks(buffer + '\n\n')
    for (const ev of events) dispatch(ev)
  }

  if (!terminal) handlers.onError('流式连接意外结束')
}

export function fetchDiaries() {
  return api.get<Diary[]>('/diaries')
}

export function fetchDiary(id: number) {
  return api.get<Diary>(`/diaries/${id}`)
}
