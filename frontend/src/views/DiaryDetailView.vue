<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast } from 'vant'
import { fetchDiary } from '../api/diaries'
import type { Diary } from '../types/domain'
import { formatChineseDate } from '../utils/date'

const route = useRoute()
const router = useRouter()
const diary = ref<Diary | null>(null)

onMounted(async () => {
  try {
    const { data } = await fetchDiary(Number(route.params.id))
    diary.value = data
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
        <van-skeleton v-if="!diary" title :row="8" />
        <article v-else class="paper-card">
          <time>{{ formatChineseDate(diary.diary_date) }}</time>
          <h1>{{ diary.title }}</h1>
          <p class="diary-content">{{ diary.content }}</p>
        </article>
      </section>
    </main>
  </div>
</template>
