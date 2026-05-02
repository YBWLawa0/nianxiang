import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { fetchMe, login as loginApi, register as registerApi } from '../api/auth'
import type { User } from '../types/domain'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('nianxiang_token') || '')
  const user = ref<User | null>(null)
  const isAuthed = computed(() => Boolean(token.value))

  async function login(username: string, password: string) {
    const { data } = await loginApi(username, password)
    token.value = data.access_token
    localStorage.setItem('nianxiang_token', token.value)
    await loadMe()
  }

  async function register(username: string, password: string) {
    await registerApi(username, password)
    await login(username, password)
  }

  async function loadMe() {
    if (!token.value) return
    const { data } = await fetchMe()
    user.value = data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('nianxiang_token')
  }

  return { token, user, isAuthed, login, register, loadMe, logout }
})
