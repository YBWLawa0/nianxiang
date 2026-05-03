<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast } from 'vant'
import { fetchDiary } from '../api/diaries'
import { useDiaryStreamStore } from '../stores/diaryStream'
import type { Diary } from '../types/domain'
import { formatChineseCalendarDate, formatChineseDate } from '../utils/date'
import { renderSafeMarkdown } from '../utils/markdown'

const DIARY_PAGE_BG_CLASS = 'diary-notebook-page-active'

const route = useRoute()
const router = useRouter()
const streamStore = useDiaryStreamStore()
const diary = ref<Diary | null>(null)
/** 生成日记进入：流式结束或直链带 write 时保持简化抬头 */
const minimalEntryChrome = ref(false)

const isWriteReveal = computed(() => route.query.write === '1')
const useMinimalHeader = computed(() => minimalEntryChrome.value || isWriteReveal.value)

/** 详情尚未拉到，但已在生成流里匹配当前 id：先展示抬头与占位，避免整页 skeleton 挡住文案 */
const earlyStreamCard = computed(
  () =>
    !diary.value &&
    isWriteReveal.value &&
    streamStore.diaryId != null &&
    streamStore.diaryId === id.value,
)

const headerDate = computed(() => {
  const dateStr = diary.value?.diary_date ?? streamStore.streamDiaryDate
  if (!dateStr) return ''
  return useMinimalHeader.value ? formatChineseCalendarDate(dateStr) : formatChineseDate(dateStr)
})

const titleText = computed(() => {
  if (useMinimalHeader.value) return '新日记'
  return diary.value?.title ?? ''
})

const id = computed(() => Number(route.params.id))

const isServerStreamForThis = computed(
  () => streamStore.diaryId != null && streamStore.diaryId === id.value,
)

const bodyText = computed(() => {
  if (!isServerStreamForThis.value) return diary.value?.content ?? ''
  if (streamStore.active) return streamStore.text
  if (!diary.value) return streamStore.text
  const fromDb = diary.value.content
  if (fromDb.length >= streamStore.text.length) return fromDb
  return streamStore.text
})

/** 流未结束或界面尚未追上服务端缓冲时显示光标（仅正文阶段） */
const showStreamCursor = computed(
  () =>
    isServerStreamForThis.value &&
    streamStore.streamPhase === 'body' &&
    (streamStore.active || streamStore.pendingTail),
)

const showOpeningHint = computed(
  () =>
    isServerStreamForThis.value &&
    streamStore.streamPhase === 'body' &&
    streamStore.waitingFirstChunk,
)

const axiangDisplay = computed(() => {
  if (isServerStreamForThis.value && (streamStore.active || streamStore.axiangText.length > 0)) {
    return streamStore.axiangText
  }
  return diary.value?.axiang_observation ?? ''
})

const ritualDisplay = computed(() => {
  if (isServerStreamForThis.value && (streamStore.active || streamStore.ritualText.length > 0)) {
    return streamStore.ritualText
  }
  return diary.value?.daily_ritual ?? ''
})

const showAxiangSection = computed(() => {
  if (!isServerStreamForThis.value) return !!(diary.value?.axiang_observation?.trim())
  if (streamStore.active && (streamStore.streamPhase === 'axiang' || streamStore.streamPhase === 'ritual')) {
    return true
  }
  if (streamStore.axiangText.length > 0) return true
  return !!(diary.value?.axiang_observation?.trim())
})

const showRitualSection = computed(() => {
  if (!isServerStreamForThis.value) return !!(diary.value?.daily_ritual?.trim())
  if (streamStore.active && streamStore.streamPhase === 'ritual') return true
  if (streamStore.ritualText.length > 0) return true
  return !!(diary.value?.daily_ritual?.trim())
})

const showAxiangCursor = computed(
  () => isServerStreamForThis.value && streamStore.active && streamStore.streamPhase === 'axiang',
)

const showRitualCursor = computed(
  () => isServerStreamForThis.value && streamStore.active && streamStore.streamPhase === 'ritual',
)

const showAxiangOpeningHint = computed(
  () =>
    isServerStreamForThis.value &&
    streamStore.streamPhase === 'axiang' &&
    streamStore.waitingFirstAxiang,
)

const showRitualOpeningHint = computed(
  () =>
    isServerStreamForThis.value &&
    streamStore.streamPhase === 'ritual' &&
    streamStore.waitingFirstRitual,
)

const axiangMdHtml = computed(() => renderSafeMarkdown(axiangDisplay.value))
const ritualMdHtml = computed(() => renderSafeMarkdown(ritualDisplay.value))

/** 正文首字前的占位：依次切换，最后一条「起草正文中」保持到首个流式字符到达 */
const OPENING_HINT_MESSAGES = [
  '正在回顾随笔......',
  '正在构思中......',
  '起草正文中......',
] as const

const AXIANG_HINT_MESSAGES = [
  '对照你的能量记录......',
  '正在读今天的碎碎念......',
  '阿响在琢磨今天的线......',
] as const

const RITUAL_HINT_MESSAGES = ['想一句能带走的话......', '收尾的小仪式......', '替你收个尾......'] as const

const openingHintIndex = ref(0)
let openingHintTimer: ReturnType<typeof setInterval> | null = null
const axiangHintIndex = ref(0)
let axiangHintTimer: ReturnType<typeof setInterval> | null = null
const ritualHintIndex = ref(0)
let ritualHintTimer: ReturnType<typeof setInterval> | null = null

function clearOpeningHintRotation() {
  if (openingHintTimer != null) {
    clearInterval(openingHintTimer)
    openingHintTimer = null
  }
  openingHintIndex.value = 0
}

function clearAxiangHintRotation() {
  if (axiangHintTimer != null) {
    clearInterval(axiangHintTimer)
    axiangHintTimer = null
  }
  axiangHintIndex.value = 0
}

function clearRitualHintRotation() {
  if (ritualHintTimer != null) {
    clearInterval(ritualHintTimer)
    ritualHintTimer = null
  }
  ritualHintIndex.value = 0
}

watch(
  () => showOpeningHint.value,
  (show) => {
    clearOpeningHintRotation()
    if (!show) return
    openingHintIndex.value = 0
    openingHintTimer = setInterval(() => {
      const last = OPENING_HINT_MESSAGES.length - 1
      if (openingHintIndex.value < last) {
        openingHintIndex.value += 1
      } else if (openingHintTimer != null) {
        clearInterval(openingHintTimer)
        openingHintTimer = null
      }
    }, 2400)
  },
  { immediate: true },
)

watch(
  () => showAxiangOpeningHint.value,
  (show) => {
    clearAxiangHintRotation()
    if (!show) return
    axiangHintIndex.value = 0
    axiangHintTimer = setInterval(() => {
      axiangHintIndex.value = (axiangHintIndex.value + 1) % AXIANG_HINT_MESSAGES.length
    }, 2400)
  },
  { immediate: true },
)

watch(
  () => showRitualOpeningHint.value,
  (show) => {
    clearRitualHintRotation()
    if (!show) return
    ritualHintIndex.value = 0
    ritualHintTimer = setInterval(() => {
      ritualHintIndex.value = (ritualHintIndex.value + 1) % RITUAL_HINT_MESSAGES.length
    }, 2400)
  },
  { immediate: true },
)

onUnmounted(() => {
  clearOpeningHintRotation()
  clearAxiangHintRotation()
  clearRitualHintRotation()
  document.documentElement.classList.remove(DIARY_PAGE_BG_CLASS)
  document.body.classList.remove(DIARY_PAGE_BG_CLASS)
})

function finishWriteReveal() {
  minimalEntryChrome.value = true
  router.replace({ name: 'diary-detail', params: { id: String(route.params.id) } })
  streamStore.reset()
}

watch(
  () => streamStore.active,
  async (active, prevActive) => {
    if (prevActive !== true || active !== false) return
    if (streamStore.diaryId !== id.value) return
    if (route.query.write !== '1') return
    try {
      const { data } = await fetchDiary(id.value)
      diary.value = data
    } catch {
      /* ignore */
    }
    finishWriteReveal()
  },
)

onMounted(async () => {
  document.documentElement.classList.add(DIARY_PAGE_BG_CLASS)
  document.body.classList.add(DIARY_PAGE_BG_CLASS)
  try {
    const { data } = await fetchDiary(id.value)
    diary.value = data
    if (isWriteReveal.value && streamStore.diaryId !== id.value) {
      minimalEntryChrome.value = true
      router.replace({ name: 'diary-detail', params: { id: String(route.params.id) } })
    }
  } catch {
    showFailToast('日记详情暂时没加载出来')
  }
})
</script>

<template>
  <div class="phone-shell">
    <main class="shell-main">
      <section class="detail-page diary-detail diary-detail--notebook page-pad">
        <van-nav-bar title="日记" left-text="返回" left-arrow @click-left="router.back()" />
        <van-skeleton v-if="!diary && !earlyStreamCard" title :row="8" />
        <div v-else class="diary-detail-layout">
          <article class="diary-detail-article">
            <time>{{ headerDate }}</time>
            <h1>{{ titleText }}</h1>
            <p class="diary-content" :class="{ 'diary-content--streaming': showStreamCursor || showOpeningHint }">
              <span v-if="showOpeningHint" class="diary-opening-hint">{{
                OPENING_HINT_MESSAGES[openingHintIndex]
              }}</span>
              {{ bodyText }}<span v-if="showStreamCursor" class="diary-stream-cursor" aria-hidden="true">▍</span>
            </p>
          </article>

          <div
            v-if="showAxiangSection || showRitualSection"
            class="diary-annotations"
          >
            <section v-if="showAxiangSection" class="diary-annotation-card diary-annotation-card--echo">
              <header class="diary-echo-card__top">
                <span class="diary-echo-card__accent" aria-hidden="true" />
                <div class="diary-echo-card__headline">
                  <span class="diary-echo-card__label-en">Echo reflection</span>
                  <span class="diary-echo-card__label-zh">阿响观察</span>
                </div>
                <span class="diary-echo-card__quote-mark" aria-hidden="true">“</span>
              </header>
              <div
                class="diary-echo-card__body"
                :class="{ 'diary-echo-card__body--streaming': showAxiangCursor || showAxiangOpeningHint }"
              >
                <p v-if="showAxiangOpeningHint" class="diary-opening-hint diary-opening-hint--on-dark">
                  {{ AXIANG_HINT_MESSAGES[axiangHintIndex] }}
                </p>
                <div class="diary-md diary-md--echo" v-html="axiangMdHtml" />
                <span v-if="showAxiangCursor" class="diary-stream-cursor diary-stream-cursor--echo" aria-hidden="true">▍</span>
              </div>
            </section>

            <section v-if="showRitualSection" class="diary-annotation-card diary-annotation-card--question">
              <header class="diary-q-card__top">
                <span class="diary-q-card__label-en">Echo · memory · truth</span>
                <span class="diary-q-card__label-zh">今日一问</span>
              </header>
              <div
                class="diary-q-card__body"
                :class="{ 'diary-q-card__body--streaming': showRitualCursor || showRitualOpeningHint }"
              >
                <p v-if="showRitualOpeningHint" class="diary-opening-hint">
                  {{ RITUAL_HINT_MESSAGES[ritualHintIndex] }}
                </p>
                <div class="diary-md" v-html="ritualMdHtml" />
                <span v-if="showRitualCursor" class="diary-stream-cursor diary-stream-cursor--block" aria-hidden="true">▍</span>
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* 与 style.css 中 :root 变量一致，保证 shell 与正文区外无白边 */
.phone-shell {
  background-color: var(--diary-notebook-paper);
  background-image: var(--diary-notebook-lines), var(--diary-notebook-wash);
}

.diary-detail--notebook {
  min-height: calc(100vh - 88px);
  background-color: var(--diary-notebook-paper);
  background-image: var(--diary-notebook-lines), var(--diary-notebook-wash);
}

.diary-detail-layout {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.diary-detail-article {
  position: relative;
  padding: 4px 2px 8px;
}

.diary-detail-article time {
  color: var(--color-ink-light);
  font-family: var(--font-mono);
  font-size: 13px;
  display: block;
  margin-bottom: 10px;
}

.diary-detail-article h1 {
  margin: 12px 0 20px;
}

.diary-annotations {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 28px;
}

.diary-annotation-card {
  min-width: 0;
  border-radius: 22px;
  padding: 14px 14px 16px;
  box-shadow: 0 6px 22px rgba(44, 36, 30, 0.1);
}

.diary-annotation-card--echo {
  position: relative;
  overflow: hidden;
  background: #453228;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 8px 28px rgba(30, 22, 18, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.diary-echo-card__top {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.diary-echo-card__accent {
  flex-shrink: 0;
  width: 4px;
  min-height: 36px;
  border-radius: 3px;
  background: linear-gradient(180deg, #e8d4b4 0%, #c4a574 100%);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.12);
}

.diary-echo-card__headline {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 2px;
}

.diary-echo-card__label-en {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: #d4b896;
}

.diary-echo-card__label-zh {
  font-family: var(--font-serif, 'Cormorant Garamond', Georgia, serif);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: rgba(255, 250, 245, 0.92);
}

.diary-echo-card__quote-mark {
  position: absolute;
  right: -6px;
  top: -18px;
  font-family: var(--font-serif, Georgia, serif);
  font-size: 72px;
  line-height: 1;
  color: rgba(0, 0, 0, 0.18);
  pointer-events: none;
  user-select: none;
}

.diary-echo-card__body {
  position: relative;
  z-index: 1;
  font-size: 15px;
  line-height: 1.75;
}

.diary-echo-card__body--streaming {
  min-height: 3em;
}

.diary-md--echo :deep(p) {
  margin: 0 0 0.65em;
  font-family: var(--font-serif, 'Cormorant Garamond', Georgia, serif);
  font-style: italic;
  font-weight: 450;
  color: rgba(255, 252, 248, 0.94);
}

.diary-md--echo :deep(p:last-child) {
  margin-bottom: 0;
}

.diary-md--echo :deep(ul),
.diary-md--echo :deep(ol) {
  margin: 0 0 0.65em;
  padding-left: 1.2em;
  color: rgba(255, 252, 248, 0.9);
  font-style: italic;
}

.diary-md--echo :deep(li) {
  margin: 0.25em 0;
}

.diary-md--echo :deep(strong) {
  font-weight: 600;
  color: #fff;
}

.diary-md--echo :deep(a) {
  color: #e8c995;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.diary-md--echo :deep(h1),
.diary-md--echo :deep(h2),
.diary-md--echo :deep(h3) {
  font-family: var(--font-serif, 'Cormorant Garamond', Georgia, serif);
  font-style: italic;
  font-weight: 600;
  color: rgba(255, 252, 248, 0.96);
  margin: 0.75em 0 0.4em;
}
.diary-md--echo :deep(h1:first-child),
.diary-md--echo :deep(h2:first-child),
.diary-md--echo :deep(h3:first-child) {
  margin-top: 0;
}

.diary-md--echo :deep(blockquote) {
  border-left-color: rgba(212, 184, 150, 0.45);
  color: rgba(255, 250, 245, 0.85);
}

.diary-md--echo :deep(code) {
  background: rgba(0, 0, 0, 0.22);
  color: rgba(255, 250, 245, 0.95);
}

.diary-md--echo :deep(pre) {
  background: rgba(0, 0, 0, 0.25);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 250, 245, 0.92);
}

.diary-stream-cursor--echo {
  color: rgba(232, 201, 149, 0.85);
}

.diary-annotation-card--question {
  background: linear-gradient(165deg, #fffcf9 0%, #f4f1eb 100%);
  border: 1px solid rgba(230, 225, 216, 0.95);
  box-shadow: 0 4px 18px rgba(44, 44, 42, 0.06);
}

.diary-q-card__top {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.diary-q-card__label-en {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(120, 112, 102, 0.72);
}

.diary-q-card__label-zh {
  font-family: var(--font-serif, 'Cormorant Garamond', Georgia, serif);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--color-ink, #2c2c2a);
}

.diary-q-card__body {
  position: relative;
  font-size: 15px;
  line-height: 1.75;
  color: var(--color-ink, #2c2c2a);
}

.diary-q-card__body--streaming {
  min-height: 3em;
}

.diary-opening-hint--on-dark {
  color: rgba(232, 213, 190, 0.78);
}

.diary-stream-cursor {
  display: inline-block;
  margin-left: 1px;
  color: var(--muted, #8a7a68);
  animation: diary-cursor-blink 0.95s step-end infinite;
  font-weight: 300;
}

@keyframes diary-cursor-blink {
  50% {
    opacity: 0;
  }
}

.diary-content--streaming {
  min-height: 6em;
}

.diary-opening-hint {
  display: block;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--muted, #9c8f84);
  letter-spacing: 0.02em;
  animation: diary-hint-pulse 1.4s ease-in-out infinite;
}

@keyframes diary-hint-pulse {
  50% {
    opacity: 0.65;
  }
}

.diary-md :deep(p) {
  margin: 0 0 0.65em;
}
.diary-md :deep(p:last-child) {
  margin-bottom: 0;
}
.diary-md :deep(ul),
.diary-md :deep(ol) {
  margin: 0 0 0.65em;
  padding-left: 1.35em;
}
.diary-md :deep(li) {
  margin: 0.25em 0;
}
.diary-md :deep(h1),
.diary-md :deep(h2),
.diary-md :deep(h3) {
  font-family: var(--font-serif, 'Cormorant Garamond', Georgia, serif);
  font-weight: 600;
  margin: 0.85em 0 0.45em;
  line-height: 1.35;
  color: var(--color-ink, #2c2c2a);
}
.diary-md :deep(h1) {
  font-size: 1.2em;
}
.diary-md :deep(h2) {
  font-size: 1.1em;
}
.diary-md :deep(h3) {
  font-size: 1.05em;
}
.diary-md :deep(h1:first-child),
.diary-md :deep(h2:first-child),
.diary-md :deep(h3:first-child) {
  margin-top: 0;
}
.diary-md :deep(blockquote) {
  margin: 0.65em 0;
  padding: 0.35em 0 0.35em 0.85em;
  border-left: 3px solid rgba(212, 163, 115, 0.45);
  color: var(--color-ink-light, #5a5a58);
}
.diary-md :deep(pre) {
  margin: 0.65em 0;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(90, 90, 90, 0.08);
  overflow-x: auto;
  font-family: var(--font-mono, monospace);
  font-size: 13px;
  line-height: 1.55;
}
.diary-md :deep(code) {
  font-family: var(--font-mono, monospace);
  font-size: 0.9em;
  padding: 0.12em 0.35em;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.55);
}
.diary-md :deep(pre code) {
  padding: 0;
  background: none;
  font-size: inherit;
}
.diary-md :deep(a) {
  color: #8b623d;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.diary-md :deep(hr) {
  margin: 1em 0;
  border: 0;
  border-top: 1px solid rgba(90, 90, 90, 0.12);
}
.diary-md :deep(strong) {
  font-weight: 600;
}

.diary-stream-cursor--block {
  display: inline-block;
  margin-top: 2px;
}
</style>
