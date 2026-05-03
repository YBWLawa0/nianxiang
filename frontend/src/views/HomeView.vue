<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFitText } from '../composables/useFitText'

const router = useRouter()
const heroTitleEl = ref<HTMLElement | null>(null)
useFitText(heroTitleEl)

function goAuth(mode: 'login' | 'register') {
  router.push({ name: 'auth', query: { mode } })
}
</script>

<template>
  <div class="phone-shell public-shell home-page">
    <section class="hero-panel">
      <p class="eyebrow">念响</p>
      <h1 ref="heroTitleEl" class="fit-text-title">把每天的心事，轻轻放回自己身边</h1>
      <p class="subtitle">
        念想陪你随手记录、随心分享，也有阿响像朋友一样回应你，帮你看见那些没来得及照顾的情绪。
      </p>
      <div class="hero-actions">
        <button class="primary-action" @click="goAuth('register')">开始记录今天</button>
        <button class="ghost-action" @click="goAuth('login')">我已有账号</button>
      </div>
    </section>

    <section class="feature-story">
      <article class="story-card record-sample">
        <div class="story-top">
          <span>随手记</span>
          <small>今天 21:38</small>
        </div>
        <p>下班路上突然觉得自己撑了很久，但看到晚霞的时候，又好像被轻轻接住了一下。</p>
      </article>

      <article class="story-card ai-sample">
        <div class="avatar">响</div>
        <div>
          <strong>阿响</strong>
          <p>我听见你今天很累，也听见你还愿意为一点光停下来。先不用急着变好，能感觉到自己，就已经很珍贵。</p>
        </div>
      </article>
    </section>

    <section class="home-grid">
      <article class="home-card">
        <span>01</span>
        <h2>语音和文字都能接住</h2>
        <p>灵感、情绪、琐事和一句没说出口的话，都可以先放在念想里。</p>
      </article>
      <article class="home-card">
        <span>02</span>
        <h2>给每段随笔一个温度</h2>
        <p>阿响会为你生成能量刻度、九宫格标签和亲近的评语，不把你分析成冷冰冰的数据。</p>
      </article>
      <article class="home-card diary-preview">
        <span>03</span>
        <h2>把一天写成自己的日记</h2>
        <p>从你的视角整理当天随笔，保留你的语气、心情和那些细小但重要的瞬间。</p>
      </article>
    </section>

    <section class="signal-panel">
      <div>
        <small>能量刻度</small>
        <div class="home-energy">
          <i class="on"></i>
          <i class="on"></i>
          <i class="on"></i>
          <i></i>
          <i></i>
        </div>
      </div>
      <div class="tag-cloud">
        <span>自我照顾</span>
        <span>微光时刻</span>
        <span>关系回声</span>
      </div>
    </section>
  </div>
</template>
