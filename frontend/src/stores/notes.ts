import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createNote as createNoteApi, fetchNotes } from '../api/notes'
import type { Note } from '../types/domain'
import { todayString } from '../utils/date'

export const useNoteStore = defineStore('notes', () => {
  const notes = ref<Note[]>([])
  const loading = ref(false)

  async function loadToday() {
    loading.value = true
    try {
      const { data } = await fetchNotes({ date: todayString() })
      notes.value = data
    } finally {
      loading.value = false
    }
  }

  async function loadAll() {
    loading.value = true
    try {
      const { data } = await fetchNotes()
      notes.value = data
    } finally {
      loading.value = false
    }
  }

  async function create(content: string) {
    const { data } = await createNoteApi(content, todayString())
    notes.value = [...notes.value, data]
    return data
  }

  return { notes, loading, loadToday, loadAll, create }
})
