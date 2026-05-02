<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { showFailToast, showLoadingToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import { useNoteStore } from '../stores/notes'
import { formatDateTime } from '../utils/date'

const router = useRouter()
const noteStore = useNoteStore()
const text = ref('')
const voiceMode = ref(false)
const recording = ref(false)
const sending = ref(false)
const recognitionRef = ref<any>(null)
const textBeforeVoice = ref('')

onMounted(() => {
  noteStore.loadToday().catch(() => showFailToast('今天的随笔暂时没加载出来'))
})

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

function startVoice() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) {
    showFailToast('当前浏览器暂不支持语音转文字')
    return
  }
  recording.value = true
  textBeforeVoice.value = text.value
  const recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.interimResults = true
  recognition.continuous = true
  recognition.onresult = (event: any) => {
    const latest = event.results[event.results.length - 1]?.[0]?.transcript || ''
    text.value = `${text.value}${latest}`
  }
  recognition.onerror = () => showFailToast('这段语音没有听清')
  recognition.start()
  recognitionRef.value = recognition
}

function endVoice(cancelled = false) {
  if (!recording.value) return
  recording.value = false
  if (recognitionRef.value) {
    recognitionRef.value.stop()
    recognitionRef.value = null
  }
  if (cancelled) {
    showFailToast('已取消这段语音')
    text.value = textBeforeVoice.value
    return
  }
}
</script>

<template>
  <section class="record-page page-pad input-page">
    <PageHeader eyebrow="Nianxiang" title="今天想留下些什么？" subtitle="一句话、一段情绪、一点念头，都可以先放在这里。" />

    <div class="timeline-wrap">
      <van-loading v-if="noteStore.loading" color="#6b7f5c">加载今日随笔...</van-loading>
      <div v-else-if="noteStore.notes.length === 0" class="empty-state">
        <span>今日还没有随笔哦</span>
        <small>先写下此刻的第一句话。</small>
      </div>
      <div v-else class="timeline-list">
        <button v-for="note in noteStore.notes" :key="note.id" class="timeline-item" @click="router.push(`/notes/${note.id}`)">
          <article class="note-snippet">
            <p class="snippet-time">{{ formatDateTime(note.created_at) }}</p>
            <p class="snippet-content">{{ note.content }}</p>
          </article>
        </button>
      </div>
    </div>

    <div class="composer">
      <button class="mode-btn" @click="voiceMode = !voiceMode">{{ voiceMode ? '文' : '声' }}</button>
      <template v-if="!voiceMode">
        <textarea v-model="text" rows="1" placeholder="随手记一笔：刚刚发生了什么？" @keydown.enter.exact.prevent="submit" />
        <button class="send-btn" :disabled="!text.trim() || sending" @click="submit">发送</button>
      </template>
      <button
        v-else
        class="voice-hold"
        :class="{ recording }"
        @pointerdown="startVoice"
        @pointerup="endVoice(false)"
        @pointerleave="endVoice(true)"
        @pointercancel="endVoice(true)"
        @contextmenu.prevent
      >
        {{ recording ? '松开发送，上滑取消' : '按住说话' }}
      </button>
    </div>
  </section>
</template>
