import api from './client'
import type { Diary } from '../types/domain'

export function generateDiary(date?: string) {
  return api.post<Diary>('/diaries/generate', { diary_date: date })
}

export function fetchDiaries() {
  return api.get<Diary[]>('/diaries')
}

export function fetchDiary(id: number) {
  return api.get<Diary>(`/diaries/${id}`)
}
