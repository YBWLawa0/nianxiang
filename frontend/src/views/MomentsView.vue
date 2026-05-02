<script setup lang="ts">
import { onMounted } from 'vue'
import { showFailToast } from 'vant'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import { useNoteStore } from '../stores/notes'
import { formatDateTime } from '../utils/date'

const router = useRouter()
const noteStore = useNoteStore()

onMounted(() => {
  noteStore.loadAll().catch(() => showFailToast('随笔墙暂时没加载出来'))
})
</script>

<template>
  <section class="page-pad moments-page">
    <PageHeader eyebrow="Moments" title="随笔墙" subtitle="像发朋友圈一样，看见自己每天留下的微小波纹。" />
    <van-loading v-if="noteStore.loading" color="#6b7f5c">加载中...</van-loading>
    <div v-else-if="noteStore.notes.length === 0" class="empty-state"><span>还没有可展示的随笔</span></div>
    <article v-for="note in noteStore.notes" v-else :key="note.id" class="moment-card" @click="router.push(`/notes/${note.id}`)">
      <div class="avatar">念</div>
      <div class="moment-body">
        <div class="moment-top"><strong class="moment-author">我</strong><span>{{ formatDateTime(note.created_at) }}</span></div>
        <p>{{ note.content }}</p>
        <div class="moment-meta"><span>能量 {{ note.energy_score }}</span><span>{{ note.grid_tag }}</span></div>
        <div v-if="note.ai_ready && note.ai_comment" class="comment">
          <strong class="comment-author">念想 AI：</strong>{{ note.ai_comment }}
        </div>
      </div>
    </article>
  </section>
</template>
