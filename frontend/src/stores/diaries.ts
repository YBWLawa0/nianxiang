import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchDiaries, generateDiary as generateDiaryApi } from '../api/diaries'
import type { Diary } from '../types/domain'
import { todayString } from '../utils/date'

export const useDiaryStore = defineStore('diaries', () => {
  const diaries = ref<Diary[]>([])
  const loading = ref(false)

  async function loadAll() {
    loading.value = true
    try {
      const { data } = await fetchDiaries()
      diaries.value = data
    } finally {
      loading.value = false
    }
  }

  async function generateToday() {
    const { data } = await generateDiaryApi(todayString())
    const index = diaries.value.findIndex((item) => item.id === data.id)
    if (index >= 0) diaries.value[index] = data
    else diaries.value = [data, ...diaries.value]
    return data
  }

  return { diaries, loading, loadAll, generateToday }
})
