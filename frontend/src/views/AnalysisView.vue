<script setup lang="ts">
import { computed, ref } from 'vue'
import { showToast } from 'vant'
import PageHeader from '../components/PageHeader.vue'

type AnalysisTab = 'week' | 'month' | 'year'

const activeTab = ref<AnalysisTab>('week')

const tabs: Array<{ key: AnalysisTab; label: string; eyebrow: string }> = [
  { key: 'week', label: '周', eyebrow: 'Reports' },
  { key: 'month', label: '月', eyebrow: 'Podcasts' },
  { key: 'year', label: '年', eyebrow: 'Bookshelf' },
]

const tabCopy = {
  week: {
    title: '一周报告',
    subtitle: '把一周里的能量起伏、反复出现的人和事，整理成几张可以慢慢翻看的报告。',
  },
  month: {
    title: '月度播客',
    subtitle: '像听一封私人电台来信，回放这个月那些被你反复提起的主题和情绪。',
  },
  year: {
    title: '年度书架',
    subtitle: '把一年装订成册，每本书都留住一个阶段的自己。',
  },
} satisfies Record<AnalysisTab, { title: string; subtitle: string }>

const activeCopy = computed(() => tabCopy[activeTab.value])
const activeEyebrow = computed(() => tabs.find((tab) => tab.key === activeTab.value)?.eyebrow || 'Insight')

const weeklyReports = [
  {
    id: 1,
    range: '4月22日 - 4月28日',
    title: '把注意力收回来的七天',
    summary: '你开始更频繁地记录“边界感”和“休息”，焦虑没有消失，但已经能被命名。',
    tags: ['能量回升', '边界', '睡眠'],
    pulse: '72%',
  },
  {
    id: 2,
    range: '4月15日 - 4月21日',
    title: '很多小事在悄悄修复你',
    summary: '散步、热茶和两次认真聊天，让这一周的低谷没有继续向下滑。',
    tags: ['修复', '陪伴'],
    pulse: '64%',
  },
  {
    id: 3,
    range: '4月8日 - 4月14日',
    title: '过载之后的慢速重启',
    summary: '任务密度偏高，身体信号出现得更早。你已经在学习把暂停当成安排的一部分。',
    tags: ['过载', '重启', '计划'],
    pulse: '48%',
  },
]

const monthlyPodcasts = [
  {
    id: 1,
    date: '2026.04',
    duration: '18 min',
    title: '四月的声音：不再把疲惫藏起来',
    summary: '本期会从三段随笔开始，聊聊你如何识别消耗、寻找可持续的节奏。',
    chapters: ['开场独白', '情绪天气', '给下个月的话'],
  },
  {
    id: 2,
    date: '2026.03',
    duration: '24 min',
    title: '三月回放：那些重新发芽的愿望',
    summary: '你在月底重新提起了创作、朋友和新的生活秩序，它们都还很轻，但已经在场。',
    chapters: ['愿望清单', '关系片段', '温柔收尾'],
  },
  {
    id: 3,
    date: '2026.02',
    duration: '15 min',
    title: '二月短节目：把冬天慢慢放下',
    summary: '春节后的节奏切换、家庭对话和迟来的休息，是这个月最常出现的三个关键词。',
    chapters: ['节奏切换', '家庭回声'],
  },
]

const yearlyBooks = [
  {
    id: 1,
    year: '2026',
    title: '柔软地向前',
    subtitle: '关于重新安排生活秩序的一年',
    color: 'sand',
  },
  {
    id: 2,
    year: '2025',
    title: '把日子写亮',
    subtitle: '从零散记录到稳定表达',
    color: 'moss',
  },
  {
    id: 3,
    year: '2024',
    title: '心事的地图',
    subtitle: '第一次看见自己的重复模式',
    color: 'clay',
  },
  {
    id: 4,
    year: '2023',
    title: '慢慢靠近自己',
    subtitle: '练习诚实，也练习休息',
    color: 'ink',
  },
]

function openPlaceholder(target: string) {
  showToast(`${target}详情页先占位，后续接入`)
}
</script>

<template>
  <section class="page-pad analysis-page">
    <PageHeader :eyebrow="activeEyebrow" :title="activeCopy.title" :subtitle="activeCopy.subtitle" />

    <nav class="analysis-tabs" aria-label="分析时间范围">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="analysis-tab"
        :class="{ 'analysis-tab--active': activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span>{{ tab.label }}</span>
        <small>{{ tab.eyebrow }}</small>
      </button>
    </nav>

    <div v-if="activeTab === 'week'" class="analysis-stack">
      <article
        v-for="report in weeklyReports"
        :key="report.id"
        class="analysis-card report-card"
        @click="openPlaceholder(report.title)"
      >
        <div class="analysis-card__meta">
          <time>{{ report.range }}</time>
          <span>{{ report.pulse }}</span>
        </div>
        <h2>{{ report.title }}</h2>
        <p>{{ report.summary }}</p>
        <div class="analysis-tags">
          <span v-for="tag in report.tags" :key="tag">{{ tag }}</span>
        </div>
      </article>
    </div>

    <div v-else-if="activeTab === 'month'" class="analysis-stack">
      <article
        v-for="podcast in monthlyPodcasts"
        :key="podcast.id"
        class="analysis-card podcast-card"
        @click="openPlaceholder(podcast.title)"
      >
        <div class="podcast-cover">
          <span>{{ podcast.date }}</span>
        </div>
        <div class="podcast-body">
          <div class="analysis-card__meta">
            <time>{{ podcast.date }}</time>
            <span>{{ podcast.duration }}</span>
          </div>
          <h2>{{ podcast.title }}</h2>
          <p>{{ podcast.summary }}</p>
          <div class="podcast-chapters">
            <span v-for="chapter in podcast.chapters" :key="chapter">{{ chapter }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="bookcase" aria-label="年度书架">
      <div v-for="book in yearlyBooks" :key="book.id" class="bookcase-slot">
        <article
          class="year-book"
          :class="`year-book--${book.color}`"
          @click="openPlaceholder(`${book.year} 年度书`)"
        >
          <span class="year-book__year">{{ book.year }}</span>
          <h2>{{ book.title }}</h2>
          <p>{{ book.subtitle }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
