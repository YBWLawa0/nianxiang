<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { showFailToast, showLoadingToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import { useNoteStore } from '../stores/notes'
import type { Note } from '../types/domain'
import { formatDateTime } from '../utils/date'

const CANCEL_SWIPE_PX = 56
const LONG_PRESS_MS = 520

let longPressTimer: ReturnType<typeof setTimeout> | null = null
const longPressTriggered = ref(false)
const activeDeleteId = ref<number | null>(null)
/** 关闭删除条时的那次 click 不跳转详情 */
const suppressNavForNoteId = ref<number | null>(null)

const router = useRouter()
const noteStore = useNoteStore()
const text = ref('')
const voiceMode = ref(false)
const recording = ref(false)
/** 松手后等待识别结束并保存时仍为 true，草稿继续显示 */
const voiceFinalizePending = ref(false)
const sending = ref(false)
const recognitionRef = ref<any>(null)
const voiceDraftText = ref('')
const voiceDraftEl = ref<HTMLElement | null>(null)
const swipeCancelled = ref(false)
const voiceSessionCancelled = ref(false)
let voiceTrackingCleanup: (() => void) | null = null
let voiceEndHandled = false

const showEmptyHint = computed(
  () => noteStore.notes.length === 0 && !recording.value && !voiceFinalizePending.value,
)
const hasVoiceDraft = computed(() => recording.value || voiceFinalizePending.value)

/** 记录页：自上而下从旧到新，最新一条在最下面（与接口 desc 存储顺序相反） */
const notesForTimeline = computed(() => [...noteStore.notes].reverse())

const draftStatusLine = computed(() => {
  if (voiceFinalizePending.value) return '正在保存…'
  if (swipeCancelled.value) return '松开手指取消'
  return '正在聆听…'
})

function clearLongPressTimer() {
  if (longPressTimer != null) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

function onNotePointerDown(note: Note) {
  if (activeDeleteId.value != null && activeDeleteId.value !== note.id) {
    activeDeleteId.value = null
  }
  clearLongPressTimer()
  longPressTriggered.value = false
  longPressTimer = setTimeout(() => {
    longPressTimer = null
    longPressTriggered.value = true
    activeDeleteId.value = note.id
  }, LONG_PRESS_MS)
}

function onNotePointerUp() {
  clearLongPressTimer()
}

function onNoteRowClick(note: Note, e: MouseEvent) {
  const t = e.target as HTMLElement
  if (t.closest('.note-dropdown-menu')) return

  if (longPressTriggered.value) {
    longPressTriggered.value = false
    e.preventDefault()
    e.stopPropagation()
    return
  }
  if (suppressNavForNoteId.value === note.id) {
    suppressNavForNoteId.value = null
    e.preventDefault()
    e.stopPropagation()
    return
  }
  router.push(`/notes/${note.id}`)
}

function onDismissDeletePointer(e: PointerEvent) {
  if (activeDeleteId.value == null) return
  const t = e.target as HTMLElement
  if (t.closest('.note-dropdown-menu')) return
  const wrap = t.closest('.timeline-note-wrap')
  const wid = wrap ? Number((wrap as HTMLElement).dataset.noteId) : NaN
  if (wrap && wid === activeDeleteId.value) {
    const id = activeDeleteId.value
    activeDeleteId.value = null
    suppressNavForNoteId.value = id
    e.preventDefault()
    return
  }
  activeDeleteId.value = null
}

async function removeNote(note: Note) {
  const toast = showLoadingToast({ message: '正在删除…', forbidClick: true, duration: 0 })
  try {
    await noteStore.remove(note.id)
    activeDeleteId.value = null
    showSuccessToast('已删除')
  } catch {
    showFailToast('删除失败，请稍后重试')
  } finally {
    toast.close()
  }
}

onMounted(() => {
  noteStore.loadToday().catch(() => showFailToast('今天的随笔暂时没加载出来'))
  document.addEventListener('pointerdown', onDismissDeletePointer, true)
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', onDismissDeletePointer, true)
  clearLongPressTimer()
  detachVoiceTracking()
  recognitionRef.value?.abort?.()
})

function detachVoiceTracking() {
  voiceTrackingCleanup?.()
  voiceTrackingCleanup = null
}

function attachVoiceTracking(startY: number) {
  detachVoiceTracking()
  const onMove = (ev: PointerEvent) => {
    const deltaUp = startY - ev.clientY
    swipeCancelled.value = deltaUp > CANCEL_SWIPE_PX
  }
  voiceTrackingCleanup = () => {
    window.removeEventListener('pointermove', onMove)
  }
  window.addEventListener('pointermove', onMove, { passive: true })
}

function getShellMain(): HTMLElement | null {
  return document.querySelector('.shell-main') as HTMLElement | null
}

function getComposerNode(): HTMLElement | null {
  return document.querySelector('.record-page .composer') as HTMLElement | null
}

/** ref 与 DOM 不同步时用选择器兜底（避免在草稿挂载前按旧高度滚到底） */
function getVoiceDraftNode(): HTMLElement | null {
  return voiceDraftEl.value ?? (document.querySelector('.record-page .voice-draft') as HTMLElement | null)
}

/** 实际滚动区域是 AppShell 的 main.shell-main */
function applyDraftScroll() {
  const main = getShellMain()
  const draft = getVoiceDraftNode()
  if (!main || !draft || !hasVoiceDraft.value) return

  const mainRect = main.getBoundingClientRect()
  const draftRect = draft.getBoundingClientRect()
  const composerTop = getComposerNode()?.getBoundingClientRect().top ?? mainRect.bottom
  const visibleTop = mainRect.top + 12
  const visibleBottom = Math.min(mainRect.bottom, composerTop) - 16

  const bottomOverflow = draftRect.bottom - visibleBottom
  if (bottomOverflow > 0) {
    main.scrollTop += bottomOverflow
  }

  const adjustedDraftTop = draft.getBoundingClientRect().top
  const topOverflow = visibleTop - adjustedDraftTop
  if (topOverflow > 0) {
    main.scrollTop -= topOverflow
  }
}

let scrollDraftRaf = 0
function scheduleApplyDraftScroll() {
  if (scrollDraftRaf) return
  scrollDraftRaf = requestAnimationFrame(() => {
    scrollDraftRaf = 0
    applyDraftScroll()
    requestAnimationFrame(applyDraftScroll)
  })
}

async function scrollDraftIntoView() {
  await nextTick()
  requestAnimationFrame(() => {
    applyDraftScroll()
    requestAnimationFrame(() => {
      applyDraftScroll()
      requestAnimationFrame(applyDraftScroll)
    })
  })
}

watch(
  [hasVoiceDraft, voiceDraftText],
  ([visible]) => {
    if (visible) scheduleApplyDraftScroll()
  },
  { flush: 'post' },
)

async function submit() {
  const content = text.value.trim()
  if (!content || sending.value) return
  sending.value = true
  const toast = showLoadingToast({ message: '正在听你说完...', forbidClick: true, duration: 0 })
  try {
    await noteStore.create(content)
    text.value = ''
    showSuccessToast('已经记下来了')
  } catch {
    showFailToast('随笔保存失败，请稍后再试')
  } finally {
    toast.close()
    sending.value = false
  }
}

async function finalizeVoiceNote(content: string) {
  if (!content || sending.value) return
  sending.value = true
  const toast = showLoadingToast({ message: '正在记下…', forbidClick: true, duration: 0 })
  try {
    await noteStore.create(content)
    showSuccessToast('已经记下来了')
  } catch {
    showFailToast('随笔保存失败，请稍后再试')
  } finally {
    toast.close()
    sending.value = false
  }
}

function startVoice(e: PointerEvent) {
  if (recording.value || voiceFinalizePending.value || sending.value) return
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) {
    showFailToast('当前浏览器暂不支持语音转文字')
    return
  }

  swipeCancelled.value = false
  voiceSessionCancelled.value = false
  voiceEndHandled = false
  voiceDraftText.value = ''
  attachVoiceTracking(e.clientY)
  recording.value = true

  void scrollDraftIntoView()

  const recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = true

  recognition.onresult = (event: any) => {
    let full = ''
    for (let i = 0; i < event.results.length; i++) {
      full += event.results[i][0].transcript
    }
    voiceDraftText.value = full
    scheduleApplyDraftScroll()
  }

  recognition.onerror = (event: any) => {
    if (event.error === 'aborted') return
    recording.value = false
    voiceFinalizePending.value = false
    voiceDraftText.value = ''
    recognitionRef.value = null
    detachVoiceTracking()
    showFailToast(event.error === 'no-speech' ? '没有听到声音，请再试一次' : '这段语音没有听清')
  }

  recognition.onend = () => {
    recognitionRef.value = null
    detachVoiceTracking()
    if (voiceEndHandled) return
    voiceEndHandled = true

    if (voiceSessionCancelled.value) {
      voiceDraftText.value = ''
      voiceFinalizePending.value = false
      voiceSessionCancelled.value = false
      showFailToast('已取消这段语音')
      swipeCancelled.value = false
      return
    }

    const content = voiceDraftText.value.trim()
    voiceDraftText.value = ''
    voiceFinalizePending.value = false

    if (!content) {
      showFailToast('没有识别到内容')
      return
    }
    void finalizeVoiceNote(content)
  }

  recognitionRef.value = recognition
  try {
    recognition.start()
  } catch {
    recording.value = false
    voiceDraftText.value = ''
    recognitionRef.value = null
    detachVoiceTracking()
    showFailToast('无法启动语音识别')
  }
}

function endVoice(explicitCancel = false) {
  if (!recording.value) return
  detachVoiceTracking()

  const cancelled = explicitCancel || swipeCancelled.value
  voiceSessionCancelled.value = cancelled
  recording.value = false

  const rec = recognitionRef.value
  if (!rec) return

  try {
    if (cancelled) {
      voiceFinalizePending.value = false
      rec.abort()
    } else {
      voiceFinalizePending.value = true
      rec.stop()
    }
  } catch {
    voiceFinalizePending.value = false
    rec.abort()
  }
}
</script>

<template>
  <section class="record-page page-pad input-page">
    <PageHeader eyebrow="念想" title="今天想留下些什么？" subtitle="一句话、一段情绪、一点念头，都可以先放在这里。" />

    <div class="timeline-wrap">
      <van-loading v-if="noteStore.loading && !hasVoiceDraft" color="#c5a028">加载今日随笔...</van-loading>
      <div v-else-if="showEmptyHint" class="empty-state">
        <span>今天还没有记录。在下方写下你的第一个想法吧。</span>
      </div>
      <div v-else class="timeline-list">
        <div
          v-for="note in notesForTimeline"
          :key="note.id"
          class="timeline-item timeline-note-wrap"
          :class="{ 'timeline-note-wrap--delete-open': activeDeleteId === note.id }"
          :data-note-id="String(note.id)"
          @pointerdown="onNotePointerDown(note)"
          @pointerup="onNotePointerUp"
          @pointercancel="onNotePointerUp"
          @click="onNoteRowClick(note, $event)"
          @contextmenu.prevent
        >
          <article class="note-snippet">
            <p class="snippet-time">{{ formatDateTime(note.created_at) }}</p>
            <p class="snippet-content">{{ note.content }}</p>
          </article>
          <div
            v-show="activeDeleteId === note.id"
            class="note-dropdown-menu"
          >
            <div 
              class="note-dropdown-item"
              @pointerdown.stop
              @click.stop="removeNote(note)"
            >
              删除
            </div>
          </div>
        </div>
        <div
          v-show="hasVoiceDraft"
          ref="voiceDraftEl"
          class="timeline-item voice-draft"
          :class="{ 'voice-draft--cancel': swipeCancelled && recording }"
        >
          <article class="note-snippet">
            <p class="snippet-time">{{ draftStatusLine }}</p>
            <p class="snippet-content voice-draft-content">
              {{ voiceDraftText || (recording ? '说出你想记下的内容…' : '…') }}
            </p>
          </article>
        </div>
      </div>
    </div>

    <div class="composer">
      <button type="button" class="mode-btn" :aria-label="voiceMode ? '切换到键盘输入' : '切换到语音输入'" @click="voiceMode = !voiceMode">
        <!-- 微信同款：四根高低不齐的圆角竖条 -->
        <svg v-if="!voiceMode" class="mode-btn-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <rect x="4" y="12" width="3" height="8" rx="1.5" />
          <rect x="9" y="7" width="3" height="13" rx="1.5" />
          <rect x="14" y="10" width="3" height="10" rx="1.5" />
          <rect x="19" y="6" width="3" height="14" rx="1.5" />
        </svg>
        <svg v-else class="mode-btn-icon" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="2.5" y="5.5" width="19" height="13" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.75" />
          <circle cx="7" cy="10" r="1.15" fill="currentColor" />
          <circle cx="12" cy="10" r="1.15" fill="currentColor" />
          <circle cx="17" cy="10" r="1.15" fill="currentColor" />
          <circle cx="9" cy="13" r="1.15" fill="currentColor" />
          <circle cx="12" cy="13" r="1.15" fill="currentColor" />
          <circle cx="15" cy="13" r="1.15" fill="currentColor" />
          <path d="M8 16h8" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" fill="none" />
        </svg>
      </button>
      <template v-if="!voiceMode">
        <textarea v-model="text" rows="1" placeholder="此刻你在想什么？" @keydown.enter.exact.prevent="submit" />
        <button class="send-btn" :disabled="!text.trim() || sending" @click="submit">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
        </button>
      </template>
      <button
        v-else
        class="voice-hold"
        :class="{ recording, 'voice-hold--cancel': swipeCancelled && recording }"
        @pointerdown.prevent="startVoice($event)"
        @pointerup="endVoice(false)"
        @pointercancel="endVoice(true)"
        @contextmenu.prevent
      >
        {{ recording ? '松开发送，上滑取消' : '按住说话' }}
      </button>
    </div>
  </section>
</template>
