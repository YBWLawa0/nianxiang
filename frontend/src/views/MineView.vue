<script setup lang="ts">
import { useRouter } from 'vue-router'
import { showSuccessToast } from 'vant'
import PageHeader from '../components/PageHeader.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.replace({ name: 'home' })
  showSuccessToast('已经退出登录')
}
</script>

<template>
  <section class="page-pad mine-page">
    <PageHeader eyebrow="Me" title="我的念想" subtitle="账号只负责保护你的记录，真正重要的是你每天怎样和自己说话。" />
    <div class="profile-card">
      <div class="avatar large">念</div>
      <div>
        <small>当前账号</small>
        <h2>{{ auth.user?.username || '已登录用户' }}</h2>
        <p>密码已加密保存，随笔与日记会按账号隔离。</p>
      </div>
      <van-button block round color="#1f3b2d" @click="logout">退出登录</van-button>
    </div>
  </section>
</template>
