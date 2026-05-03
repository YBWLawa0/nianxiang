import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { DiaryStreamPhase } from '../api/diaries'

/** 从服务端流入的正文存在 rawText，界面展示 text（限速「吐字」，避免大块一次性刷出） */
export const useDiaryStreamStore = defineStore('diaryStream', () => {
  const diaryId = ref<number | null>(null)
  /** SSE meta 里的日记日期，详情接口未返回前用于抬头 */
  const streamDiaryDate = ref<string | null>(null)
  /** 服务端累计全文 */
  const rawText = ref('')
  /** 用户可见的已「写出」部分 */
  const text = ref('')
  /** 当前 SSE 阶段：正文 → 阿响观察 → 今日一问与收尾 */
  const streamPhase = ref<'body' | DiaryStreamPhase>('body')
  /** 阿响观察 / 今日一问 分段流式（直接拼接，不再做吐字延迟） */
  const axiangText = ref('')
  const ritualText = ref('')
  const active = ref(false)

  let drainTimer: ReturnType<typeof setTimeout> | null = null

  const waitingFirstChunk = computed(() => active.value && rawText.value.length === 0)

  const waitingFirstAxiang = computed(
    () => active.value && streamPhase.value === 'axiang' && axiangText.value.length === 0,
  )

  const waitingFirstRitual = computed(
    () => active.value && streamPhase.value === 'ritual' && ritualText.value.length === 0,
  )

  /** 正文尚未全部映到界面（用于光标：流结束 flush 前也可能为 true） */
  const pendingTail = computed(() => rawText.value.length > text.value.length)

  function clearDrain() {
    if (drainTimer !== null) {
      clearTimeout(drainTimer)
      drainTimer = null
    }
  }

  /** 单步延时：积压越多略加快，避免永远追不上；换行与标点略停顿 */
  function nextDelay(raw: string, posBefore: number): number {
    const lag = raw.length - posBefore
    if (lag > 200) return 18 + Math.random() * 14
    if (lag > 90) return 28 + Math.random() * 18
    const ch = raw[posBefore] ?? ''
    if (ch === '\n') return 240 + Math.random() * 160
    if (/[，。！？、；：]/.test(ch)) return 95 + Math.random() * 75
    if (ch === ' ') return 18 + Math.random() * 12
    return 46 + Math.random() * 38
  }

  /** 本步吐出字符数：积压大时略多字，仍保持可读节奏 */
  function charsThisStep(raw: string, curLen: number): number {
    const lag = raw.length - curLen
    if (lag > 220) return 3
    if (lag > 100) return 2
    return 1
  }

  function scheduleDrain() {
    if (drainTimer !== null) return
    const tick = () => {
      const raw = rawText.value
      const cur = text.value.length
      if (cur >= raw.length) {
        drainTimer = null
        return
      }
      const n = charsThisStep(raw, cur)
      text.value = raw.slice(0, Math.min(cur + n, raw.length))
      const delay = nextDelay(raw, cur)
      drainTimer = window.setTimeout(tick, delay)
    }
    drainTimer = window.setTimeout(tick, 0)
  }

  function start() {
    clearDrain()
    diaryId.value = null
    streamDiaryDate.value = null
    rawText.value = ''
    text.value = ''
    streamPhase.value = 'body'
    axiangText.value = ''
    ritualText.value = ''
    active.value = true
  }

  function reset() {
    clearDrain()
    diaryId.value = null
    streamDiaryDate.value = null
    rawText.value = ''
    text.value = ''
    streamPhase.value = 'body'
    axiangText.value = ''
    ritualText.value = ''
    active.value = false
  }

  function bindDiary(id: number, diaryDateIso?: string) {
    diaryId.value = id
    if (diaryDateIso) streamDiaryDate.value = diaryDateIso
  }

  function append(chunk: string) {
    if (!chunk) return
    rawText.value += chunk
    scheduleDrain()
  }

  function setStreamPhase(phase: DiaryStreamPhase) {
    if (phase === 'axiang') {
      flushDisplay()
      streamPhase.value = 'axiang'
      return
    }
    streamPhase.value = 'ritual'
  }

  function appendAxiang(chunk: string) {
    if (!chunk) return
    axiangText.value += chunk
  }

  function appendRitual(chunk: string) {
    if (!chunk) return
    ritualText.value += chunk
  }

  /** 流结束：立刻对齐到全文，避免收尾卡顿 */
  function flushDisplay() {
    clearDrain()
    text.value = rawText.value
  }

  function setActive(v: boolean) {
    active.value = v
  }

  return {
    diaryId,
    streamDiaryDate,
    rawText,
    text,
    streamPhase,
    axiangText,
    ritualText,
    active,
    waitingFirstChunk,
    waitingFirstAxiang,
    waitingFirstRitual,
    pendingTail,
    start,
    reset,
    bindDiary,
    append,
    setStreamPhase,
    appendAxiang,
    appendRitual,
    flushDisplay,
    setActive,
  }
})
