<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const active = computed({
  get: () => String(route.name || 'record'),
  set: (name: string) => router.push({ name }),
})
</script>

<template>
  <div class="phone-shell">
    <main
      class="shell-main"
      :class="{ 'shell-main--record': route.name === 'record' || route.name === 'moments' }"
    >
      <router-view />
    </main>
    <van-tabbar v-model="active" route class="bottom-nav" active-color="#1f3b2d" inactive-color="#9c8f84">
      <van-tabbar-item name="record" to="/record" icon="edit">记录</van-tabbar-item>
      <van-tabbar-item name="moments" to="/moments" icon="friends-o">随笔</van-tabbar-item>
      <van-tabbar-item name="diaries" to="/diaries" icon="notes-o">日记</van-tabbar-item>
      <van-tabbar-item name="analysis" to="/analysis" icon="chart-trending-o">分析</van-tabbar-item>
      <van-tabbar-item name="mine" to="/mine" icon="manager-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>
