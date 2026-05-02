export interface PodcastTrack {
  id: string
  title: string
  /** 相对于站点根路径，如 /播客-四合一.mp3 */
  src: string
}

export interface MonthlyPodcast {
  id: number
  date: string
  monthDisplay: string
  duration: string
  /** 念想的「…月收录」标题 —— 不含主题词，主题在 tags */
  title: string
  summary: string
  /** 主题等标签（与语音标题一致，来自文件名） */
  tags: string[]
  coverImage: string
  /** 每档播客仅一段语音 */
  tracks: PodcastTrack[]
}

/** 标题里「xxx的…月收录」的 xxx，可随产品名修改 */
export const PODCAST_COLLECTION_BRAND = '念想'

/** 与 public 根目录下「播客-*.mp3」文件名对应的语音标题（不含扩展名与前缀） */
export function podcastTitleFromSrc(src: string): string {
  const base = src.replace(/^.*\//, '').replace(/\.mp3$/i, '')
  const m = base.match(/^播客-(.+)$/)
  return m?.[1] ?? base
}

const MONTH_ZH = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'] as const

/** 如 2026.04 → 四月 */
export function formatMonthOnlyZh(dateDot: string): string {
  const m = parseInt(dateDot.split('.')[1] || '0', 10)
  if (m < 1 || m > 12) return dateDot
  return `${MONTH_ZH[m]}月`
}

export function formatMonthZh(dateDot: string): string {
  const [y, m] = dateDot.split('.')
  if (!y || !m) return dateDot
  return `${y}年${parseInt(m, 10)}月`
}

function buildCollectionTitle(dateDot: string): string {
  return `${PODCAST_COLLECTION_BRAND}的${formatMonthOnlyZh(dateDot)}收录`
}

/** public 根目录下的统一播客封面 */
const PODCAST_COVER = '/播客封面.jpg'

type SegmentDef = { id: number; dateDot: string; src: string }

/** public 中 5 段语音；前四期为 2026 年 1–4 月，第五期为 2025 年 12 月（单月单主题） */
const segments: SegmentDef[] = [
  { id: 1, dateDot: '2026.01', src: '/播客-面对矛盾.mp3' },
  { id: 2, dateDot: '2026.02', src: '/播客-时间错位.mp3' },
  { id: 3, dateDot: '2026.03', src: '/播客-时间停止.mp3' },
  { id: 4, dateDot: '2026.04', src: '/播客-发量影响.mp3' },
  { id: 5, dateDot: '2025.12', src: '/播客-四合一.mp3' },
]

export const monthlyPodcasts: MonthlyPodcast[] = segments.map((s) => {
  const theme = podcastTitleFromSrc(s.src)
  const track: PodcastTrack = {
    id: `t-${s.id}`,
    title: theme,
    src: s.src,
  }
  return {
    id: s.id,
    date: s.dateDot,
    monthDisplay: formatMonthZh(s.dateDot),
    duration: '单集',
    title: buildCollectionTitle(s.dateDot),
    summary: '本月私人电台单集；当期主题见下方标签。',
    tags: [theme],
    coverImage: PODCAST_COVER,
    tracks: [track],
  }
})

/** 全部播客按日期从新到旧（列表不按月份筛选，仅排序展示） */
export function podcastsNewestFirst(): MonthlyPodcast[] {
  return [...monthlyPodcasts].sort((a, b) => b.date.localeCompare(a.date))
}

export function getMonthlyPodcastById(id: number): MonthlyPodcast | undefined {
  return monthlyPodcasts.find((p) => p.id === id)
}
