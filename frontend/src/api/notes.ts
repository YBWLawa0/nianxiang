import api from './client'
import type { Note } from '../types/domain'

export function createNote(content: string, recordDate?: string) {
  return api.post<Note>('/notes', { content, record_date: recordDate })
}

export function fetchNotes(params?: { date?: string }) {
  return api.get<Note[]>('/notes', { params })
}

export function fetchNote(id: number) {
  return api.get<Note>(`/notes/${id}`)
}
