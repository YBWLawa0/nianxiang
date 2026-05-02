<script setup lang="ts">
import { onMounted } from 'vue'
import { showFailToast } from 'vant'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import { useNoteStore } from '../stores/notes'
import type { EnergyScore } from '../types/domain'
import { formatDateTime } from '../utils/date'

const router = useRouter()
const noteStore = useNoteStore()

function clampEnergy(score: number): EnergyScore {
  const n = Math.round(Number(score))
  if (n < 1) return 1
  if (n > 5) return 5
  return n as EnergyScore
}

function energyBarWidthPercent(score: number): string {
  return `${(clampEnergy(score) / 5) * 100}%`
}

onMounted(() => {
  noteStore.loadAll().catch(() => showFailToast('随笔墙暂时没加载出来'))
})
</script>

<template>
  <section class="page-pad moments-page">
    <PageHeader eyebrow="Moments" title="随笔墙" subtitle="像发朋友圈一样，看见自己每天留下的微小波纹。" />
    <van-loading v-if="noteStore.loading" color="#c5a028">加载中...</van-loading>
    <div v-else-if="noteStore.notes.length === 0" class="empty-state"><span>还没有可展示的随笔</span></div>
    <article v-for="note in noteStore.notes" v-else :key="note.id" class="moment-card" @click="router.push(`/notes/${note.id}`)">
      <div class="avatar">念</div>
      <div class="moment-body">
        <div class="moment-top"><strong class="moment-author">我</strong><span>{{ formatDateTime(note.created_at) }}</span></div>
        <p>{{ note.content }}</p>
        <div class="moment-meta">
          <div
            class="moment-energy-bar"
            role="img"
            :aria-label="`能量 ${clampEnergy(note.energy_score)} / 5`"
          >
            <div class="moment-energy-bar__track">
              <div
                class="moment-energy-bar__fill"
                :class="`moment-energy-bar__fill--${clampEnergy(note.energy_score)}`"
                :style="{ width: energyBarWidthPercent(note.energy_score) }"
              />
            </div>
          </div>
          <span class="moment-grid-tag">{{ note.grid_tag }}</span>
        </div>

        <div v-if="note.ai_ready && note.ai_comment" class="comment">
          <strong class="comment-author">念想 AI：</strong>{{ note.ai_comment }}
        </div>
      </div>
    </article>
  </section>
</template>
