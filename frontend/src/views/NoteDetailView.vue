<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast } from 'vant'
import { fetchNote } from '../api/notes'
import type { Note } from '../types/domain'
import { formatChineseDate } from '../utils/date'

const route = useRoute()
const router = useRouter()
const note = ref<Note | null>(null)
let timer: number | null = null

async function loadDetail() {
  const { data } = await fetchNote(Number(route.params.id))
  note.value = data
  if (data.ai_ready && timer) {
    clearInterval(timer)
    timer = null
  }
}

onMounted(async () => {
  try {
    await loadDetail()
    if (!note.value?.ai_ready) {
      timer = window.setInterval(() => {
        loadDetail().catch(() => void 0)
      }, 2500)
    }
  } catch {
    showFailToast('随笔详情暂时没加载出来')
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="phone-shell">
    <main class="shell-main shell-main--record">
      <section class="detail-page page-pad">
        <van-nav-bar title="随笔详情" left-text="返回" left-arrow @click-left="router.back()" />
        <van-skeleton v-if="!note" title :row="5" />
        <article v-else class="detail-card">
          <p class="eyebrow">{{ formatChineseDate(note.record_date) }}</p>
          <h1>{{ note.content }}</h1>
          <template v-if="note.ai_ready">
            <div :class="['energy-scale', `energy-score--${note.energy_score}`]">
              <span v-for="n in 5" :key="n" :class="{ on: n <= note.energy_score }"></span>
            </div>
            <div class="detail-grid">
              <div><small>能量刻度</small><strong>{{ note.energy_score }} / 5</strong></div>
              <div><small>九宫格板块</small><strong>{{ note.grid_tag }}</strong></div>
            </div>
            <div class="ai-reply">
              <small>阿响想对你说</small>
              <p>{{ note.ai_comment }}</p>
            </div>
          </template>
          <div v-else class="draft-hint">
            <small>阿响正在为你分析这条随笔</small>
            <p>草稿已保存，稍后会自动补充能量刻度、九宫格标签和阿响的评语。</p>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>
