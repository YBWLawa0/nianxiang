<script setup lang="ts">
import * as echarts from 'echarts/core'
import { LineChart, RadarChart } from 'echarts/charts'
import { GridComponent, RadarComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, RadarChart, GridComponent, RadarComponent, CanvasRenderer])
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showFailToast } from 'vant'
import { getWeeklyReportDetail } from '../data/weeklyReportDetails'

const BROWN = '#6D4C41'
const TAN_AXIS = '#C5B4A2'
const RADAR_GRID = 'rgba(74, 55, 40, 0.12)'

const route = useRoute()
const router = useRouter()

const lineRef = ref<HTMLElement | null>(null)
const radarRef = ref<HTMLElement | null>(null)
let lineInst: echarts.ECharts | null = null
let radarInst: echarts.ECharts | null = null

const detail = computed(() => {
  const id = Number(route.params.id)
  return Number.isFinite(id) ? getWeeklyReportDetail(id) : undefined
})

function disposeCharts() {
  lineInst?.dispose()
  radarInst?.dispose()
  lineInst = null
  radarInst = null
}

function lineOption() {
  const d = detail.value
  if (!d) return {}
  return {
    animationDuration: 480,
    grid: { left: 4, right: 8, top: 12, bottom: 8 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: d.energyLabels,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: TAN_AXIS, fontSize: 11, fontFamily: 'var(--font-sans)' },
    },
    yAxis: {
      type: 'value',
      show: false,
      scale: true,
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 3, color: BROWN },
        data: d.energySeries,
      },
    ],
  }
}

function radarOption() {
  const d = detail.value
  if (!d) return {}
  return {
    animationDuration: 520,
    radar: {
      center: ['50%', '52%'],
      radius: '62%',
      indicator: d.radarIndicators.map((name) => ({ name, max: 100 })),
      axisName: {
        color: BROWN,
        fontSize: 11,
        fontFamily: 'var(--font-sans)',
        lineHeight: 14,
      },
      splitLine: { lineStyle: { color: RADAR_GRID } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: RADAR_GRID } },
    },
    series: [
      {
        type: 'radar',
        symbol: 'none',
        data: [
          {
            value: d.radarValues,
            areaStyle: { color: 'rgba(109, 76, 65, 0.22)' },
            lineStyle: { width: 2, color: BROWN },
          },
        ],
      },
    ],
  }
}

function resizeCharts() {
  lineInst?.resize()
  radarInst?.resize()
}

function syncCharts() {
  const d = detail.value
  if (!d || !lineRef.value || !radarRef.value) return
  if (!lineInst) lineInst = echarts.init(lineRef.value)
  if (!radarInst) radarInst = echarts.init(radarRef.value)
  lineInst.setOption(lineOption(), true)
  radarInst.setOption(radarOption(), true)
}

watch(
  () => [detail.value, route.params.id] as const,
  async () => {
    if (!detail.value) return
    await nextTick()
    syncCharts()
    resizeCharts()
  },
  { flush: 'post' },
)

onMounted(async () => {
  if (!detail.value) {
    showFailToast('找不到该周报告')
    router.back()
    return
  }
  window.addEventListener('resize', resizeCharts)
  await nextTick()
  syncCharts()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeCharts()
})
</script>

<template>
  <div class="phone-shell weekly-report-shell">
    <main class="shell-main">
      <section class="weekly-detail page-pad">
        <van-nav-bar title="" left-text="返回" left-arrow class="weekly-detail__nav" @click-left="router.back()" />

        <template v-if="detail">
          <header class="weekly-detail__hero">
            <p class="weekly-detail__kicker">EMOTIONAL ANALYTICS</p>
            <h1 class="weekly-detail__title">周度情感报告</h1>
            <p class="weekly-detail__range">{{ detail.range }}</p>
          </header>

          <!-- 能量涨落 -->
          <article class="weekly-card weekly-card--light">
            <div class="weekly-card__head">
              <div class="weekly-card__label">
                <span class="weekly-ico weekly-ico--trend" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M4 18h16M7 14l3-4 3 2 4-6"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>
                <span>能量涨落</span>
              </div>
              <div class="weekly-card__stat">
                <strong>{{ detail.avgIndex.toFixed(1) }}</strong>
                <small>AVG INDEX</small>
              </div>
            </div>
            <div ref="lineRef" class="weekly-chart weekly-chart--line" role="img" aria-label="一周能量曲线" />
          </article>

          <!-- 人生罗盘 -->
          <article class="weekly-card weekly-card--light weekly-card--radar">
            <div class="weekly-card__head weekly-card__head--center">
              <div class="weekly-card__label">
                <span class="weekly-ico weekly-ico--target" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6" />
                    <circle cx="12" cy="12" r="5.5" stroke="currentColor" stroke-width="1.4" />
                    <circle cx="12" cy="12" r="2" fill="currentColor" />
                  </svg>
                </span>
                <span>人生罗盘</span>
              </div>
            </div>
            <div ref="radarRef" class="weekly-chart weekly-chart--radar" role="img" aria-label="人生罗盘雷达图" />
          </article>

          <!-- 深度洞察 -->
          <article class="weekly-card weekly-card--insight">
            <div class="weekly-insight__brand">
              <span class="weekly-ico weekly-ico--brain" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M12 4c-2.5 0-4.5 1.6-5.2 3.8-.8-.3-1.7-.2-2.4.3-.9.6-1.4 1.7-1.4 2.9 0 .8.3 1.5.7 2.1-.4.7-.7 1.5-.7 2.4 0 1.6.9 3 2.2 3.7-.1.3-.2.7-.2 1.1 0 2.2 1.8 4 4 4h7c2.5 0 4.5-2 4.5-4.5 0-.9-.3-1.7-.7-2.4.7-.9 1.2-2 1.2-3.2 0-1.1-.4-2.1-1.1-2.9.3-.6.4-1.2.4-1.9 0-2.5-2-4.5-4.5-4.5-.3-2.3-2.3-4-4.7-4Z"
                    stroke="currentColor"
                    stroke-width="1.3"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M9.5 12.5h5M10 9.5h4.5M10 15.5h4"
                    stroke="currentColor"
                    stroke-width="1.1"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
              <span class="weekly-insight__brand-text">DEEP NEURAL INSIGHT</span>
            </div>
            <p class="weekly-insight__body">{{ detail.insightText }}</p>
            <div class="weekly-insight__highlight">
              <div class="weekly-insight__highlight-text">
                <span class="weekly-insight__tag">{{ detail.resonanceLabel }}</span>
                <strong>{{ detail.resonanceTitle }}</strong>
              </div>
              <span class="weekly-ico weekly-ico--spark" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.9 2.9M15.5 15.5l2.9 2.9M5.6 18.4l2.9-2.9M15.5 8.5l2.9-2.9"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
            </div>
          </article>

          <!-- 下周建议 -->
          <article class="weekly-card weekly-card--suggest">
            <div class="weekly-suggest__icon-wrap" aria-hidden="true">
              <span class="weekly-ico weekly-ico--bolt">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M13 2 4 14h7l-1 8 10-14h-7l0-6Z"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </div>
            <div class="weekly-suggest__body">
              <h2 class="weekly-suggest__title">下周律动建议</h2>
              <p class="weekly-suggest__text">
                <template v-for="(part, i) in detail.suggestionParts" :key="i">
                  <strong v-if="part.emphasis" class="weekly-suggest__em">{{ part.text }}</strong>
                  <template v-else>{{ part.text }}</template>
                </template>
              </p>
            </div>
          </article>
        </template>

        <van-skeleton v-else title :row="4" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.weekly-report-shell {
  background: var(--weekly-cream, #f9f7f2);
}

.weekly-detail {
  --weekly-brown: #6d4c41;
  --weekly-tan: #c5b4a2;
  --weekly-cream: #f9f7f2;
  --weekly-dark: #4b3621;
  --weekly-on-dark: #f5e6d3;
  min-height: 100%;
  padding-bottom: 120px;
  background: var(--weekly-cream);
}

.weekly-detail__nav {
  margin: -8px -12px 8px;
  background: transparent;
}

.weekly-detail__nav :deep(.van-nav-bar__content) {
  background: transparent;
}

.weekly-detail__hero {
  margin-bottom: 22px;
}

.weekly-detail__kicker {
  margin: 0 0 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.24em;
  color: var(--weekly-tan);
  text-transform: uppercase;
}

.weekly-detail__title {
  margin: 0;
  font-family: var(--font-sans);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--weekly-brown);
  line-height: 1.2;
}

.weekly-detail__range {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--weekly-tan);
}

.weekly-card {
  border-radius: 36px;
  margin-bottom: 18px;
}

.weekly-card--light {
  padding: 22px 22px 18px;
  background: #fff;
  box-shadow: 0 12px 40px rgba(44, 44, 42, 0.06);
}

.weekly-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 6px;
}

.weekly-card__head--center {
  justify-content: center;
  margin-bottom: 4px;
}

.weekly-card__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--weekly-brown);
}

.weekly-card__stat {
  text-align: right;
}

.weekly-card__stat strong {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: var(--weekly-brown);
  font-variant-numeric: tabular-nums;
}

.weekly-card__stat small {
  display: block;
  margin-top: 6px;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--weekly-tan);
  text-transform: uppercase;
}

.weekly-ico {
  display: inline-flex;
  color: var(--weekly-brown);
}

.weekly-ico svg {
  width: 22px;
  height: 22px;
}

.weekly-ico--trend svg {
  width: 20px;
  height: 20px;
}

.weekly-chart--line {
  height: 200px;
  width: 100%;
}

.weekly-card--radar {
  padding-bottom: 12px;
}

.weekly-chart--radar {
  height: 300px;
  width: 100%;
}

.weekly-card--insight {
  padding: 24px 22px 22px;
  background: var(--weekly-dark);
  color: var(--weekly-on-dark);
  box-shadow: 0 16px 48px rgba(44, 44, 42, 0.12);
}

.weekly-insight__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.weekly-ico--brain {
  color: var(--weekly-on-dark);
  opacity: 0.95;
}

.weekly-insight__brand-text {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  color: var(--weekly-on-dark);
  opacity: 0.9;
}

.weekly-insight__body {
  margin: 0 0 20px;
  font-family: var(--font-serif);
  font-size: 1.125rem;
  line-height: 1.75;
  color: var(--weekly-on-dark);
  letter-spacing: 0.02em;
}

.weekly-insight__highlight {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 16px 16px 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(245, 230, 211, 0.2);
}

.weekly-insight__tag {
  display: block;
  margin-bottom: 6px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--weekly-tan);
  text-transform: uppercase;
}

.weekly-insight__highlight-text strong {
  display: block;
  font-family: var(--font-sans);
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.35;
}

.weekly-ico--spark {
  flex-shrink: 0;
  color: var(--weekly-on-dark);
  opacity: 0.85;
}

.weekly-ico--spark svg {
  width: 28px;
  height: 28px;
}

.weekly-card--suggest {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  padding: 22px 20px;
  background: #fff;
  box-shadow: 0 10px 36px rgba(0, 0, 0, 0.05);
}

.weekly-suggest__icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: #f3efe8;
}

.weekly-ico--bolt {
  color: var(--weekly-brown);
}

.weekly-ico--bolt svg {
  width: 26px;
  height: 26px;
}

.weekly-suggest__title {
  margin: 0 0 10px;
  font-family: var(--font-sans);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--weekly-brown);
}

.weekly-suggest__text {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: #666;
}

.weekly-suggest__em {
  font-weight: 700;
  color: #4a3728;
}
</style>
