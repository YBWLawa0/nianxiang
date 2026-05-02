import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('../views/HomeView.vue'), meta: { publicOnly: true } },
    { path: '/auth', name: 'auth', component: () => import('../views/AuthView.vue'), meta: { publicOnly: true } },
    {
      path: '/',
      component: () => import('../views/AppShell.vue'),
      children: [
        { path: 'record', name: 'record', component: () => import('../views/RecordView.vue'), meta: { requiresAuth: true } },
        { path: 'moments', name: 'moments', component: () => import('../views/MomentsView.vue'), meta: { requiresAuth: true } },
        { path: 'diaries', name: 'diaries', component: () => import('../views/DiariesView.vue'), meta: { requiresAuth: true } },
        { path: 'analysis', name: 'analysis', component: () => import('../views/AnalysisView.vue'), meta: { requiresAuth: true } },
        { path: 'mine', name: 'mine', component: () => import('../views/MineView.vue'), meta: { requiresAuth: true } },
      ],
    },
    { path: '/notes/:id', name: 'note-detail', component: () => import('../views/NoteDetailView.vue'), meta: { requiresAuth: true } },
    { path: '/diaries/:id', name: 'diary-detail', component: () => import('../views/DiaryDetailView.vue'), meta: { requiresAuth: true } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const guestAllowedRouteNames = new Set(['home', 'auth'])
  if (auth.token && !auth.user) {
    try {
      await auth.loadMe()
    } catch {
      auth.logout()
    }
  }
  if (!auth.isAuthed && !guestAllowedRouteNames.has(String(to.name ?? ''))) {
    return { name: 'home' }
  }
  if (to.meta.publicOnly && auth.isAuthed) {
    return { name: 'record' }
  }
})

export default router
