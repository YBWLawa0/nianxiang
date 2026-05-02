<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { showConfirmDialog, showFailToast, showLoadingToast, showSuccessToast } from 'vant'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'
import { useDiaryStore } from '../stores/diaries'
import { formatChineseDate } from '../utils/date'

const router = useRouter()
const diaryStore = useDiaryStore()
const generating = ref(false)

onMounted(() => {
  diaryStore.loadAll().catch(() => showFailToast('日记列表暂时没加载出来'))
})

async function generate() {
  try {
    await showConfirmDialog({ title: '生成本日日记', message: '我会整理今天的随笔，用你的视角写成一篇日记。' })
  } catch {
    return
  }
  generating.value = true
  const toast = showLoadingToast({ message: '正在生成日记中...', forbidClick: true, duration: 0 })
  try {
    const diary = await diaryStore.generateToday()
    showSuccessToast('今天的日记写好了')
    router.push(`/diaries/${diary.id}`)
  } catch {
    showFailToast('日记生成失败，请确认今天已有随笔')
  } finally {
    toast.close()
    generating.value = false
  }
}
</script>

<template>
  <section class="page-pad diaries-page">
    <PageHeader eyebrow="Diary" title="把今天写成一封给自己的信" subtitle="日记会贴近你的心情和语言习惯，而不是冷冰冰的总结。" />
    <button class="generate-card" :disabled="generating" @click="generate">
      <span>生成本日日记</span>
      <small>从今日随笔中提炼情绪、事件和自我对话</small>
    </button>
    <van-loading v-if="diaryStore.loading" color="#6b7f5c">加载日记...</van-loading>
    <div v-else class="diary-list">
      <article v-for="diary in diaryStore.diaries" :key="diary.id" class="diary-card" @click="router.push(`/diaries/${diary.id}`)">
        <time>{{ formatChineseDate(diary.diary_date) }}</time>
        <h2>{{ diary.title }}</h2>
        <p>{{ diary.summary }}</p>
      </article>
    </div>
  </section>
</template>
