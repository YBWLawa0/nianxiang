<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast } from 'vant'
import { fetchDiary } from '../api/diaries'
import { useDiaryStreamStore } from '../stores/diaryStream'
import type { Diary } from '../types/domain'
import { formatChineseCalendarDate, formatChineseDate } from '../utils/date'

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

const OPENING_HINT_MESSAGES = [
  '重看一遍今天的随笔......',
  '正在构思中......',
  '正在把今天的随笔理顺......',
  '重新审查......',
  '正在起草中......',
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
      <section class="detail-page diary-detail page-pad">
        <van-nav-bar title="日记" left-text="返回" left-arrow @click-left="router.back()" />
        <van-skeleton v-if="!diary && !earlyStreamCard" title :row="8" />
        <article v-else class="paper-card diary-detail-article">
          <time>{{ headerDate }}</time>
          <h1>{{ titleText }}</h1>
          <p class="diary-content" :class="{ 'diary-content--streaming': showStreamCursor || showOpeningHint }">
            <span v-if="showOpeningHint" class="diary-opening-hint">{{
              OPENING_HINT_MESSAGES[openingHintIndex]
            }}</span>
            {{ bodyText }}<span v-if="showStreamCursor" class="diary-stream-cursor" aria-hidden="true">▍</span>
          </p>

          <section v-if="showAxiangSection" class="diary-extras">
            <h2 class="diary-extras__title">阿响观察</h2>
            <p
              class="diary-extras__body"
              :class="{ 'diary-extras__body--streaming': showAxiangCursor || showAxiangOpeningHint }"
            >
              <span v-if="showAxiangOpeningHint" class="diary-opening-hint">{{
                AXIANG_HINT_MESSAGES[axiangHintIndex]
              }}</span>
              {{ axiangDisplay }}<span v-if="showAxiangCursor" class="diary-stream-cursor" aria-hidden="true">▍</span>
            </p>
          </section>

          <section v-if="showRitualSection" class="diary-extras diary-extras--ritual">
            <h2 class="diary-extras__title">今日一问</h2>
            <p
              class="diary-extras__body"
              :class="{ 'diary-extras__body--streaming': showRitualCursor || showRitualOpeningHint }"
            >
              <span v-if="showRitualOpeningHint" class="diary-opening-hint">{{
                RITUAL_HINT_MESSAGES[ritualHintIndex]
              }}</span>
              {{ ritualDisplay }}<span v-if="showRitualCursor" class="diary-stream-cursor" aria-hidden="true">▍</span>
            </p>
          </section>
        </article>
      </section>
    </main>
  </div>
</template>

<style scoped>
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

.diary-extras {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(139, 125, 107, 0.22);
}

.diary-extras--ritual {
  margin-top: 22px;
  padding-top: 18px;
}

.diary-extras__title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--muted, #7a6c62);
  margin: 0 0 12px;
}

.diary-extras__body {
  margin: 0;
  font-size: 16px;
  line-height: 1.75;
  color: var(--text, #3d3530);
  white-space: pre-wrap;
}

.diary-extras__body--streaming {
  min-height: 3em;
}
</style>
