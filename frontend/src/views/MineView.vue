<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showToast } from 'vant'
import { useAuthStore } from '../stores/auth'

const MINE_BG_CLASS = 'mine-page-active'

const auth = useAuthStore()
const router = useRouter()

function devHint(feature: string) {
  showToast(`${feature}功能正在开发中……`)
}

function logout() {
  auth.logout()
  router.replace({ name: 'home' })
  showSuccessToast('已经退出登录')
}

onMounted(() => {
  document.documentElement.classList.add(MINE_BG_CLASS)
  document.body.classList.add(MINE_BG_CLASS)
})

onUnmounted(() => {
  document.documentElement.classList.remove(MINE_BG_CLASS)
  document.body.classList.remove(MINE_BG_CLASS)
})
</script>

<template>
  <section class="mine-page">
    <div class="user-profile-section">
      <div class="avatar-container">
        <div class="avatar-circle">
          <span>{{ (auth.user?.username || 'U').charAt(0).toUpperCase() }}</span>
        </div>
        <div class="avatar-badge">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z"/>
            <circle cx="6" cy="18" r="1.5" fill="currentColor" stroke="none" />
            <circle cx="18" cy="6" r="1.5" fill="currentColor" stroke="none" />
          </svg>
        </div>
      </div>
      <h1 class="user-name">{{ auth.user?.username || '探索者' }}</h1>
      <div class="user-id">USER ID: {{ auth.user?.id ? String(auth.user.id).padStart(4, '0') + '-QX' : '8829-QX' }}</div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="8" r="5"/>
            <path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"/>
          </svg>
        </div>
        <div class="stat-label">记录勋章</div>
        <div class="stat-value">12 Days</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="8" width="16" height="12" rx="2"/>
            <path d="M8 4h8a2 2 0 0 1 2 2v2"/>
            <path d="M16 14h-4"/>
          </svg>
        </div>
        <div class="stat-label">情感积分</div>
        <div class="stat-value">1200</div>
      </div>
    </div>

    <div class="settings-list">
      <div class="settings-item" @click="devHint('隐私设置')">
        <div class="settings-item-left">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span>隐私设置</span>
        </div>
        <van-icon name="arrow" color="#D4C9BC" />
      </div>
      <div class="settings-divider"></div>
      <div class="settings-item" @click="devHint('推送通知')">
        <div class="settings-item-left">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span>推送通知</span>
        </div>
        <van-icon name="arrow" color="#D4C9BC" />
      </div>
      <div class="settings-divider"></div>
      <div class="settings-item" @click="devHint('帮助与反馈')">
        <div class="settings-item-left">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <circle cx="12" cy="17" r="1" fill="currentColor" stroke="none"/>
          </svg>
          <span>帮助与反馈</span>
        </div>
        <van-icon name="arrow" color="#D4C9BC" />
      </div>
      <div class="settings-divider"></div>
      <div class="settings-item" @click="devHint('系统通用')">
        <div class="settings-item-left">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span>系统通用</span>
        </div>
        <van-icon name="arrow" color="#D4C9BC" />
      </div>
    </div>

    <div class="subscription-card">
      <div class="sub-header">
        <span class="sub-title">订阅计划</span>
        <span class="pro-badge">PRO</span>
      </div>
      <p class="sub-desc">已开启无限记录、月度情感播客及云端同步服务。</p>
      <button type="button" class="manage-btn" @click="devHint('管理订阅')">管理订阅</button>
    </div>

    <button type="button" class="logout-link" @click="logout">退出登录</button>
  </section>
</template>

<style scoped>
.mine-page {
  min-height: 100vh;
  background-color: var(--mine-page-bg);
  padding: 64px 24px 120px;
  font-family: var(--font-sans);
  position: relative;
  z-index: 1;
}

.mine-page::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: var(--mine-page-bg);
  z-index: -1;
}

.user-profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 2;
}

.avatar-container {
  position: relative;
  margin-bottom: 20px;
}

.avatar-circle {
  width: 104px;
  height: 104px;
  background-color: #8E6A4B;
  border-radius: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 32px rgba(142, 106, 75, 0.15);
}

.avatar-circle span {
  color: #FFFFFF;
  font-size: 46px;
  font-weight: 600;
  font-family: var(--font-sans);
}

.avatar-badge {
  position: absolute;
  right: -6px;
  bottom: -6px;
  width: 40px;
  height: 40px;
  background-color: #FFFFFF;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8E6A4B;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.user-name {
  font-size: 28px;
  font-weight: 800;
  color: #4A3A2E;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.user-id {
  font-size: 13px;
  color: #C4B5A5;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
  position: relative;
  z-index: 2;
}

.stat-card {
  background-color: #FFFFFF;
  border-radius: 40px;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02);
}

.stat-icon {
  color: #C4B5A5;
  margin-bottom: 20px;
}

.stat-label {
  font-size: 13px;
  color: #A89F91;
  font-weight: 600;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #4A3A2E;
}

.settings-list {
  background-color: #FFFFFF;
  border-radius: 40px;
  padding: 12px 28px;
  margin-bottom: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02);
  position: relative;
  z-index: 2;
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.settings-item:active {
  opacity: 0.7;
}

.settings-item-left {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #A89F91;
}

.settings-item-left span {
  font-size: 16px;
  font-weight: 600;
  color: #7A6E62;
}

.settings-divider {
  height: 1px;
  background-color: var(--mine-page-bg);
  margin: 0;
}

.subscription-card {
  background-color: #FFFFFF;
  border-radius: 40px;
  padding: 32px 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02);
  position: relative;
  z-index: 2;
}

.sub-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.sub-title {
  font-size: 17px;
  font-weight: 800;
  color: #8E6A4B;
}

.pro-badge {
  background-color: #F5EBE1;
  color: #8E6A4B;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 100px;
  letter-spacing: 0.5px;
}

.sub-desc {
  font-size: 15px;
  color: #A89F91;
  line-height: 1.6;
  margin: 0 0 28px 0;
}

.manage-btn {
  width: 100%;
  background-color: #8E6A4B;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: 600;
  padding: 18px;
  border-radius: 20px;
  border: none;
  outline: none;
  transition: transform 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 8px 20px rgba(142, 106, 75, 0.2);
}

.manage-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.logout-link {
  display: block;
  width: 100%;
  margin-top: 28px;
  padding: 12px;
  background: none;
  border: none;
  font-size: 15px;
  font-weight: 600;
  color: #C4B5A5;
  cursor: pointer;
  transition: color 0.2s ease;
}

.logout-link:active {
  color: #A89F91;
}
</style>
