<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import PageHeader from '../components/PageHeader.vue'
import { podcastsNewestFirst } from '../data/monthlyPodcasts'

const router = useRouter()

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
    title: '播客',
    subtitle: '全部单集收录于此，按时间从新到旧排列；标题仅标示月份，当期主题在标签中。',
  },
  year: {
    title: '年度书架',
    subtitle: '把一年装订成册，每本书都留住一个阶段的自己。',
  },
} satisfies Record<AnalysisTab, { title: string; subtitle: string }>

const activeCopy = computed(() => tabCopy[activeTab.value])
const activeEyebrow = computed(() => tabs.find((tab) => tab.key === activeTab.value)?.eyebrow || 'Insight')

const podcastListAll = computed(() => podcastsNewestFirst())

const weeklyReports = [
  {
    id: 1,
    coverImage: '/图片1.png',
    range: '4月22日 - 4月28日',
    title: '把注意力收回来的七天',
    summary: '你开始更频繁地记录“边界感”和“休息”，焦虑没有消失，但已经能被命名。',
    tags: ['能量回升', '边界', '睡眠'],
    pulse: '72%',
  },
  {
    id: 2,
    coverImage: '/图片2.png',
    range: '4月15日 - 4月21日',
    title: '很多小事在悄悄修复你',
    summary: '散步、热茶和两次认真聊天，让这一周的低谷没有继续向下滑。',
    tags: ['修复', '陪伴'],
    pulse: '64%',
  },
  {
    id: 3,
    coverImage: '/图片3.png',
    range: '4月8日 - 4月14日',
    title: '过载之后的慢速重启',
    summary: '任务密度偏高，身体信号出现得更早。你已经在学习把暂停当成安排的一部分。',
    tags: ['过载', '重启', '计划'],
    pulse: '48%',
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

function openWeeklyReport(id: number) {
  router.push({ name: 'weekly-report-detail', params: { id: String(id) } })
}

function showYearBookComingSoon(year: string) {
  showToast(`${year}专属年度书籍即将上线`)
}

function openPodcast(id: number) {
  router.push({ name: 'podcast-player', params: { id: String(id) } })
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
        @click="openWeeklyReport(report.id)"
      >
        <div class="report-card__cover">
          <img :src="report.coverImage" :alt="report.title" loading="lazy" decoding="async" />
        </div>
        <div class="report-card__body">
          <div class="analysis-card__meta">
            <time>{{ report.range }}</time>
            <span>{{ report.pulse }}</span>
          </div>
          <h2>{{ report.title }}</h2>
          <p>{{ report.summary }}</p>
          <div class="analysis-tags">
            <span v-for="tag in report.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else-if="activeTab === 'month'" class="analysis-stack">
      <article
        v-for="podcast in podcastListAll"
        :key="podcast.id"
        class="analysis-card podcast-card"
        @click="openPodcast(podcast.id)"
      >
        <div class="podcast-cover">
          <img
            :src="podcast.coverImage"
            :alt="podcast.title"
            loading="lazy"
            decoding="async"
          />
        </div>
        <div class="podcast-body">
          <div class="analysis-card__meta">
            <time>{{ podcast.date }}</time>
            <span>{{ podcast.duration }}</span>
          </div>
          <h2>{{ podcast.title }}</h2>
          <p>{{ podcast.summary }}</p>
          <div class="analysis-tags">
            <span v-for="tag in podcast.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="bookcase" aria-label="年度书架">
      <div v-for="book in yearlyBooks" :key="book.id" class="bookcase-slot">
        <article
          class="year-book"
          :class="`year-book--${book.color}`"
          @click="showYearBookComingSoon(book.year)"
        >
          <span class="year-book__year">{{ book.year }}</span>
          <h2>{{ book.title }}</h2>
          <p>{{ book.subtitle }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
