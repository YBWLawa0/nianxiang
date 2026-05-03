<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import type { MonthlyPodcast, PodcastTrack } from '../data/monthlyPodcasts'
import { getMonthlyPodcastById } from '../data/monthlyPodcasts'

const ACCENT_RED = '#E54D42'
const BG = '#2c2c2e'

const route = useRoute()
const router = useRouter()

const podcast = ref<MonthlyPodcast | null>(null)
const queue = ref<PodcastTrack[]>([])
const currentIndex = ref(0)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playlistOpen = ref(false)
const playlistTab = ref<'now' | 'history'>('now')
const loopMode = ref<'off' | 'list' | 'one'>('list')

const audioRef = ref<HTMLAudioElement | null>(null)

const currentTrack = computed(() => queue.value[currentIndex.value])
const progress = computed(() =>
  duration.value > 0 ? Math.min(1, currentTime.value / duration.value) : 0,
)
const playedPercent = computed(() => Math.round(progress.value * 100))

function pad2(n: number) {
  return n < 10 ? `0${n}` : String(n)
}

function formatClock(sec: number) {
  if (!Number.isFinite(sec) || sec < 0) return '00:00'
  const s = Math.floor(sec)
  const m = Math.floor(s / 60)
  const r = s % 60
  return `${pad2(m)}:${pad2(r)}`
}

function setAudioSrc() {
  const a = audioRef.value
  const t = currentTrack.value
  if (!a || !t) return
  a.src = t.src
  a.load()
}

function loadPodcast(id: number) {
  const p = getMonthlyPodcastById(id)
  if (!p || !p.tracks.length) {
    showToast('未找到该播客')
    router.replace({ name: 'analysis' })
    return
  }
  podcast.value = p
  queue.value = p.tracks.map((t) => ({ ...t }))
  currentIndex.value = 0
  currentTime.value = 0
  duration.value = 0
  playing.value = false
  playlistTab.value = 'now'
  void nextTick(() => setAudioSrc())
}

function togglePlay() {
  const a = audioRef.value
  if (!a || !currentTrack.value) return
  if (playing.value) {
    a.pause()
    playing.value = false
  } else {
    void a.play().then(
      () => {
        playing.value = true
      },
      () => {
        showToast('无法播放，请检查音频文件')
      },
    )
  }
}

function seekBy(deltaSec: number) {
  const a = audioRef.value
  if (!a || !Number.isFinite(a.duration)) return
  a.currentTime = Math.max(0, Math.min(a.duration, a.currentTime + deltaSec))
}

function onSeekInput(e: Event) {
  const a = audioRef.value
  if (!a || !duration.value) return
  const v = Number((e.target as HTMLInputElement).value)
  a.currentTime = (v / 1000) * duration.value
}

function playAfterSkip() {
  void nextTick(() => {
    void audioRef.value
      ?.play()
      .then(() => {
        playing.value = true
      })
      .catch(() => {
        playing.value = false
      })
  })
}

function goPrev() {
  if (queue.value.length <= 1) return
  const wasPlaying = playing.value
  currentIndex.value = currentIndex.value <= 0 ? queue.value.length - 1 : currentIndex.value - 1
  if (wasPlaying) playAfterSkip()
}

function goNext() {
  if (queue.value.length <= 1) return
  const wasPlaying = playing.value
  currentIndex.value = currentIndex.value >= queue.value.length - 1 ? 0 : currentIndex.value + 1
  if (wasPlaying) playAfterSkip()
}

function onEnded() {
  if (loopMode.value === 'one') {
    const a = audioRef.value
    if (a) {
      a.currentTime = 0
      void a.play().then(() => {
        playing.value = true
      })
    }
    return
  }
  if (loopMode.value === 'list' && queue.value.length >= 1) {
    const next = currentIndex.value >= queue.value.length - 1 ? 0 : currentIndex.value + 1
    currentIndex.value = next
    void nextTick(() => {
      void audioRef.value
        ?.play()
        .then(() => {
          playing.value = true
        })
        .catch(() => {
          playing.value = false
        })
    })
    return
  }
  playing.value = false
}

function cycleLoopMode() {
  loopMode.value = loopMode.value === 'off' ? 'list' : loopMode.value === 'list' ? 'one' : 'off'
}

const loopLabel = computed(() => {
  if (loopMode.value === 'list') return '列表循环'
  if (loopMode.value === 'one') return '单曲循环'
  return '顺序播放'
})

function playTrackAt(index: number) {
  if (index < 0 || index >= queue.value.length) return
  currentIndex.value = index
  void nextTick(() => {
    void audioRef.value
      ?.play()
      .then(() => {
        playing.value = true
      })
      .catch(() => {
        showToast('无法播放')
      })
  })
}

function removeFromQueue(index: number) {
  if (index < 0 || index >= queue.value.length) return
  queue.value.splice(index, 1)
  if (queue.value.length === 0) {
    playing.value = false
    audioRef.value?.pause()
    showToast('播放列表已空')
    return
  }
  if (index < currentIndex.value) {
    currentIndex.value -= 1
  } else if (index === currentIndex.value) {
    currentIndex.value = Math.min(currentIndex.value, queue.value.length - 1)
  }
}

function onTimeUpdate() {
  const a = audioRef.value
  if (!a) return
  currentTime.value = a.currentTime
}

function onLoadedMeta() {
  const a = audioRef.value
  if (!a) return
  duration.value = a.duration || 0
}

async function sharePodcast() {
  const p = podcast.value
  if (!p) return
  const url = typeof window !== 'undefined' ? window.location.href : ''
  try {
    if (navigator.share) {
      await navigator.share({ title: p.title, text: p.summary, url })
    } else {
      await navigator.clipboard.writeText(url)
      showToast('链接已复制')
    }
  } catch {
    showToast('分享已取消')
  }
}

function openPlaylist() {
  playlistOpen.value = true
}

watch(
  () => route.params.id,
  (id) => {
    const n = Number(id)
    if (Number.isFinite(n)) loadPodcast(n)
  },
  { immediate: true },
)

watch(currentIndex, () => {
  void nextTick(() => setAudioSrc())
})

watch(queue, () => {
  if (currentIndex.value >= queue.value.length) {
    currentIndex.value = Math.max(0, queue.value.length - 1)
  }
})

onMounted(() => {
  const a = audioRef.value
  if (a) {
    a.addEventListener('timeupdate', onTimeUpdate)
    a.addEventListener('loadedmetadata', onLoadedMeta)
    a.addEventListener('ended', onEnded)
  }
  void nextTick(() => setAudioSrc())
})

onUnmounted(() => {
  const a = audioRef.value
  if (a) {
    a.removeEventListener('timeupdate', onTimeUpdate)
    a.removeEventListener('loadedmetadata', onLoadedMeta)
    a.removeEventListener('ended', onEnded)
  }
})
</script>

<template>
  <div class="podcast-player" :style="{ '--podcast-red': ACCENT_RED, '--podcast-bg': BG }">
    <audio ref="audioRef" preload="metadata" playsinline />

    <header class="podcast-player__top">
      <button type="button" class="podcast-player__icon-btn" aria-label="返回" @click="router.back()">
        <van-icon name="arrow-down" />
      </button>
      <span class="podcast-player__top-title">播客</span>
      <button type="button" class="podcast-player__icon-btn" aria-label="分享" @click="sharePodcast">
        <van-icon name="share-o" />
      </button>
    </header>

    <div v-if="podcast" class="podcast-player__body">
      <div class="podcast-player__cover-wrap">
        <img class="podcast-player__cover" :src="podcast.coverImage" :alt="podcast.title" />
      </div>

      <h1 class="podcast-player__episode-title">{{ podcast.title }}</h1>
      <p v-if="currentTrack" class="podcast-player__theme">{{ currentTrack.title }}</p>
      <p class="podcast-player__month">{{ podcast.monthDisplay }}</p>

      <div class="podcast-player__seek-row">
        <button type="button" class="podcast-player__skip" aria-label="后退15秒" @click="seekBy(-15)">
          <span class="podcast-player__skip-ring">15</span>
        </button>

        <div class="podcast-player__progress-block">
          <input
            class="podcast-player__range"
            type="range"
            min="0"
            max="1000"
            :value="Math.round(progress * 1000)"
            aria-label="播放进度"
            @input="onSeekInput"
          />
          <div class="podcast-player__times">
            <span>{{ formatClock(currentTime) }}</span>
            <span>{{ formatClock(duration) }}</span>
          </div>
        </div>

        <button type="button" class="podcast-player__skip" aria-label="前进30秒" @click="seekBy(30)">
          <span class="podcast-player__skip-ring podcast-player__skip-ring--fwd">30</span>
        </button>
      </div>

      <div class="podcast-player__controls">
        <button type="button" class="podcast-player__ctrl" aria-label="音效">
          <van-icon name="music-o" />
        </button>
        <button type="button" class="podcast-player__ctrl" aria-label="上一首" @click="goPrev">
          <van-icon name="arrow-left" />
        </button>
        <button
          type="button"
          class="podcast-player__play"
          :aria-label="playing ? '暂停' : '播放'"
          @click="togglePlay"
        >
          <van-icon :name="playing ? 'pause' : 'play'" />
        </button>
        <button
          type="button"
          class="podcast-player__ctrl podcast-player__ctrl--mirror"
          aria-label="下一首"
          @click="goNext"
        >
          <van-icon name="arrow-left" />
        </button>
        <button type="button" class="podcast-player__ctrl" aria-label="播放列表" @click="openPlaylist">
          <van-icon name="orders-o" />
        </button>
      </div>

      <button type="button" class="podcast-player__detail-hint" @click="openPlaylist">
        详情
        <van-icon name="arrow-up" />
      </button>
    </div>

    <van-popup
      v-model:show="playlistOpen"
      position="bottom"
      round
      :style="{ height: '72%', padding: '0' }"
      class="podcast-playlist-popup"
    >
      <div class="playlist-sheet">
        <div class="playlist-tabs">
          <button
            type="button"
            class="playlist-tab"
            :class="{ 'playlist-tab--active': playlistTab === 'now' }"
            @click="playlistTab = 'now'"
          >
            当前播放<sup class="playlist-tab__cnt">{{ queue.length }}</sup>
          </button>
          <button
            type="button"
            class="playlist-tab"
            :class="{ 'playlist-tab--active': playlistTab === 'history' }"
            @click="playlistTab = 'history'"
          >
            历史播放
          </button>
        </div>

        <div v-if="playlistTab === 'now'" class="playlist-toolbar">
          <button type="button" class="playlist-loop" @click="cycleLoopMode">
            <van-icon name="replay" />
            <span>{{ loopLabel }}</span>
          </button>
          <div class="playlist-toolbar__icons">
            <van-icon name="wap-nav" />
            <van-icon name="success" />
            <van-icon name="delete-o" />
          </div>
        </div>

        <ul v-if="playlistTab === 'now'" class="playlist-list" aria-label="当前播放列表">
          <li
            v-for="(tr, idx) in queue"
            :key="tr.id"
            class="playlist-item"
            :class="{ 'playlist-item--active': idx === currentIndex }"
            @click="playTrackAt(idx)"
          >
            <span v-if="idx === currentIndex" class="playlist-item__wave" aria-hidden="true">▮▮</span>
            <div class="playlist-item__text">
              <div class="playlist-item__title">{{ tr.title }}</div>
              <div class="playlist-item__sub">
                <template v-if="idx === currentIndex">
                  {{ podcast?.monthDisplay }} {{ formatClock(duration) }}
                  <template v-if="duration > 0"> 已播{{ playedPercent }}%</template>
                </template>
                <template v-else>{{ podcast?.monthDisplay }} ——</template>
              </div>
            </div>
            <span v-if="idx === currentIndex" class="playlist-item__source">来源</span>
            <button
              type="button"
              class="playlist-item__remove"
              aria-label="从列表移除"
              @click.stop="removeFromQueue(idx)"
            >
              ×
            </button>
          </li>
        </ul>

        <div v-else class="playlist-empty">
          <p>暂无历史记录</p>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.podcast-player {
  min-height: 100vh;
  background: var(--podcast-bg);
  color: #f5f5f7;
  font-family: var(--font-sans);
  padding: 10px 18px 28px;
  padding-bottom: max(28px, env(safe-area-inset-bottom));
}

.podcast-player__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0 18px;
}

.podcast-player__top-title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.podcast-player__icon-btn {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: transparent;
  color: #f5f5f7;
  font-size: 20px;
}

.podcast-player__body {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  max-width: 420px;
  margin: 0 auto;
}

.podcast-player__cover-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 22px;
}

.podcast-player__cover {
  width: min(78vw, 320px);
  aspect-ratio: 1;
  border-radius: 20px;
  object-fit: cover;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.45);
}

.podcast-player__episode-title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 600;
  line-height: 1.3;
  color: #fff;
}

.podcast-player__theme {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.72);
}

.podcast-player__month {
  margin: 0 0 26px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.55);
}

.podcast-player__seek-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.podcast-player__skip {
  flex: 0 0 auto;
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  background: transparent;
  color: rgba(255, 255, 255, 0.85);
}

.podcast-player__skip-ring {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  font-size: 11px;
  font-weight: 600;
  display: grid;
  place-items: center;
  transform: rotate(-12deg);
}

.podcast-player__skip-ring--fwd {
  transform: rotate(12deg);
}

.podcast-player__progress-block {
  flex: 1;
  min-width: 0;
}

.podcast-player__range {
  width: 100%;
  height: 4px;
  appearance: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  cursor: pointer;
}

.podcast-player__range::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.2);
}

.podcast-player__range::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  border: 0;
}

.podcast-player__times {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  font-variant-numeric: tabular-nums;
}

.podcast-player__controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 22px;
  padding: 0 4px;
}

.podcast-player__ctrl {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  background: transparent;
  color: rgba(255, 255, 255, 0.85);
  font-size: 22px;
}

.podcast-player__play {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 30px;
}

.podcast-player__detail-hint {
  margin-top: auto;
  padding: 28px 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.playlist-sheet {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  color: #1c1c1e;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.playlist-tabs {
  display: flex;
  border-bottom: 1px solid #e8e8ea;
  padding: 0 8px;
}

.playlist-tab {
  flex: 1;
  padding: 16px 8px 12px;
  background: none;
  font-size: 15px;
  color: #8e8e93;
  position: relative;
}

.playlist-tab--active {
  color: #1c1c1e;
  font-weight: 700;
}

.playlist-tab--active::after {
  content: '';
  position: absolute;
  left: 20%;
  right: 20%;
  bottom: 0;
  height: 3px;
  background: #1c1c1e;
  border-radius: 2px;
}

.playlist-tab__cnt {
  font-size: 11px;
  margin-left: 2px;
}

.playlist-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 8px;
  font-size: 14px;
  color: #3a3a3c;
}

.playlist-loop {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  color: inherit;
}

.playlist-toolbar__icons {
  display: flex;
  gap: 18px;
  color: #8e8e93;
  font-size: 20px;
}

.playlist-list {
  list-style: none;
  margin: 0;
  padding: 0 0 24px;
  overflow-y: auto;
  flex: 1;
}

.playlist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid #f2f2f7;
  cursor: pointer;
}

.playlist-item--active .playlist-item__title {
  color: var(--podcast-red);
  font-weight: 600;
}

.playlist-item__wave {
  flex: 0 0 auto;
  font-size: 10px;
  color: var(--podcast-red);
  letter-spacing: -2px;
}

.playlist-item__text {
  flex: 1;
  min-width: 0;
}

.playlist-item__title {
  font-size: 15px;
  color: #1c1c1e;
  margin-bottom: 4px;
}

.playlist-item__sub {
  font-size: 12px;
  color: #8e8e93;
}

.playlist-item__source {
  flex: 0 0 auto;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f2f2f7;
  color: #8e8e93;
}

.playlist-item__remove {
  flex: 0 0 auto;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: none;
  color: #c7c7cc;
  font-size: 22px;
  line-height: 1;
}

.playlist-empty {
  padding: 32px 20px;
  text-align: center;
  color: #8e8e93;
  font-size: 14px;
}

.podcast-player__ctrl--mirror :deep(.van-icon) {
  transform: scaleX(-1);
}

/* van-popup 内容区白底 */
:deep(.podcast-playlist-popup.van-popup) {
  background: #fff;
}
</style>
