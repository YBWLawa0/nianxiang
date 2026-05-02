/** 周度报告详情（与设计稿结构对应；后续可对接接口） */

export type WeeklyReportDetail = {
  id: number
  range: string
  headline: string
  energyLabels: string[]
  energySeries: number[]
  avgIndex: number
  radarIndicators: string[]
  radarValues: number[]
  insightText: string
  resonanceLabel: string
  resonanceTitle: string
  suggestionParts: Array<{ text: string; emphasis?: boolean }>
}

const radarIndicators = [
  '身体健康',
  '财务理财',
  '人际社交',
  '工作事业',
  '家庭生活',
  '学习成长',
  '体验突破',
  '休闲娱乐',
] as const

export const weeklyReportDetails: WeeklyReportDetail[] = [
  {
    id: 1,
    range: '4月22日 - 4月28日',
    headline: '把注意力收回来的七天',
    energyLabels: ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    energySeries: [3.2, 2.9, 3.6, 3.3, 3.9, 4.2],
    avgIndex: 3.8,
    radarIndicators: [...radarIndicators],
    radarValues: [72, 58, 45, 68, 76, 64, 55, 62],
    insightText:
      '在本周的律动中，你如同在大雾中独自航行的船只，虽然方向明确，但社交的缺失让你的灵性雷达有些暗淡。',
    resonanceLabel: 'HIGH RESONANCE',
    resonanceTitle: '周六露营时刻',
    suggestionParts: [
      { text: '下周你的工作项目进入收尾阶段，建议预留 ' },
      { text: '20%', emphasis: true },
      { text: ' 的缓冲时间应对突发；每天至少留出 ' },
      { text: '30', emphasis: true },
      { text: ' 分钟散步，帮助神经系统从「紧绷命名」平缓过渡到「可持续节奏」。' },
    ],
  },
  {
    id: 2,
    range: '4月15日 - 4月21日',
    headline: '很多小事在悄悄修复你',
    energyLabels: ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    energySeries: [3.0, 3.2, 2.9, 3.5, 3.3, 3.8],
    avgIndex: 3.3,
    radarIndicators: [...radarIndicators],
    radarValues: [78, 62, 70, 58, 82, 60, 52, 74],
    insightText:
      '散步、热茶与两次认真聊天，像细线把散落的一天轻轻串起；低谷没有继续下滑，本身就是一种修复。',
    resonanceLabel: 'HIGH RESONANCE',
    resonanceTitle: '周三夜里的那通电话',
    suggestionParts: [
      { text: '下周试着把「陪伴」写进日程而不只是心情：每周固定 ' },
      { text: '2', emphasis: true },
      { text: ' 次短对话 + ' },
      { text: '1', emphasis: true },
      { text: ' 次无屏幕散步，观察能量曲线是否更平稳。' },
    ],
  },
  {
    id: 3,
    range: '4月8日 - 4月14日',
    headline: '过载之后的慢速重启',
    energyLabels: ['Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    energySeries: [2.2, 2.0, 2.3, 2.5, 2.8, 2.9],
    avgIndex: 2.5,
    radarIndicators: [...radarIndicators],
    radarValues: [55, 48, 52, 78, 60, 58, 50, 44],
    insightText:
      '任务密度偏高时，身体往往比头脑更早说话；你已经开始把暂停当作安排的一部分，这是重启的语法。',
    resonanceLabel: 'HIGH RESONANCE',
    resonanceTitle: '周五提前结束的清单',
    suggestionParts: [
      { text: '进入下一周前，为每天划定「硬停止」时间，晚间屏幕亮度下调并预留不少于 ' },
      { text: '7', emphasis: true },
      { text: ' 小时睡眠窗口；需要冲刺时，用番茄钟把深度工作压缩到清醒时段的 ' },
      { text: '40%', emphasis: true },
      { text: '。' },
    ],
  },
]

const byId = new Map<number, WeeklyReportDetail>(weeklyReportDetails.map((d) => [d.id, d]))

export function getWeeklyReportDetail(id: number): WeeklyReportDetail | undefined {
  return byId.get(id)
}
