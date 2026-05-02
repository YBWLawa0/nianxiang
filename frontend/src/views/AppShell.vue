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
  <div class="phone-shell app-shell">
    <!-- Desktop Sidebar -->
    <aside class="desktop-sidebar">
      <div class="sidebar-logo">Echoes</div>
      <nav class="sidebar-nav">
        <router-link to="/record" class="sidebar-item" active-class="sidebar-item--active">
          <van-icon name="edit" /> 记录
        </router-link>
        <router-link to="/moments" class="sidebar-item" active-class="sidebar-item--active">
          <van-icon name="friends-o" /> 随笔
        </router-link>
        <router-link to="/diaries" class="sidebar-item" active-class="sidebar-item--active">
          <van-icon name="notes-o" /> 日记
        </router-link>
        <router-link to="/analysis" class="sidebar-item" active-class="sidebar-item--active">
          <van-icon name="chart-trending-o" /> 分析
        </router-link>
        <router-link to="/mine" class="sidebar-item" active-class="sidebar-item--active">
          <van-icon name="manager-o" /> 我的
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <main
      class="shell-main"
      :class="{ 'shell-main--record': route.name === 'record' }"
    >
      <router-view />
    </main>

    <!-- Mobile Bottom Nav -->
    <van-tabbar v-model="active" route class="bottom-nav" active-color="#D4A373" inactive-color="#5A5A58">
      <van-tabbar-item name="record" to="/record" icon="edit">记录</van-tabbar-item>
      <van-tabbar-item name="moments" to="/moments" icon="friends-o">随笔</van-tabbar-item>
      <van-tabbar-item name="diaries" to="/diaries" icon="notes-o">日记</van-tabbar-item>
      <van-tabbar-item name="analysis" to="/analysis" icon="chart-trending-o">分析</van-tabbar-item>
      <van-tabbar-item name="mine" to="/mine" icon="manager-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>
