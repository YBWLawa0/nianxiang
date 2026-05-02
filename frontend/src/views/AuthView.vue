<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast, showSuccessToast } from 'vant'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const mode = ref<'login' | 'register'>(route.query.mode === 'register' ? 'register' : 'login')
const submitting = ref(false)

watch(
  () => route.query.mode,
  (nextMode) => {
    mode.value = nextMode === 'register' ? 'register' : 'login'
  },
)

watch(mode, (nextMode) => {
  if (route.query.mode !== nextMode) {
    router.replace({ query: { ...route.query, mode: nextMode } })
  }
})

function redirectAfterAuth() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  router.replace(redirect.startsWith('/') && !redirect.startsWith('/auth') ? redirect : '/record')
}

async function submit() {
  const account = username.value.trim()
  const secret = password.value.trim()
  if (!account) {
    showFailToast('先给自己留一个账号名')
    return
  }
  if (secret.length < 6) {
    showFailToast('密码至少需要 6 位')
    return
  }
  submitting.value = true
  try {
    if (mode.value === 'login') await auth.login(account, secret)
    else await auth.register(account, secret)
    showSuccessToast(mode.value === 'login' ? '欢迎回来' : '账号已创建')
    redirectAfterAuth()
  } catch (error: any) {
    const message = error?.response?.data?.detail
    showFailToast(message || (mode.value === 'login' ? '登录失败，请检查账号和密码' : '注册失败，请稍后再试'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="phone-shell public-shell auth-page">
    <button class="back-home" @click="router.push('/')">回到首页</button>

    <section class="auth-hero">
      <p class="eyebrow">Me</p>
      <h1>先把自己领回来</h1>
      <p class="subtitle">账号只负责保护你的记录，真正重要的是你每天怎样和自己说话。</p>
    </section>

    <form class="auth-card standalone" @submit.prevent="submit">
      <van-tabs v-model:active="mode" shrink color="#1f3b2d">
        <van-tab name="login" title="登录" />
        <van-tab name="register" title="注册" />
      </van-tabs>
      <van-field v-model="username" label="账号" placeholder="输入你的账号" autocomplete="username" />
      <van-field
        v-model="password"
        label="密码"
        type="password"
        placeholder="至少 6 位"
        :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
      />
      <van-button block round color="#1f3b2d" native-type="submit" :loading="submitting">
        {{ mode === 'login' ? '登录' : '注册并登录' }}
      </van-button>
    </form>

    <p class="auth-footnote">
      {{ mode === 'login' ? '回来看看今天的自己。' : '从一条随笔开始，慢慢长出你的自我对话。' }}
    </p>
  </div>
</template>
