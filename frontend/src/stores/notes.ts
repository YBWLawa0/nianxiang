import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createNote as createNoteApi, deleteNote as deleteNoteApi, fetchNotes } from '../api/notes'
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
    notes.value = [data, ...notes.value]
    return data
  }

  async function remove(id: number) {
    await deleteNoteApi(id)
    notes.value = notes.value.filter((n) => n.id !== id)
  }

  return { notes, loading, loadToday, loadAll, create, remove }
})
