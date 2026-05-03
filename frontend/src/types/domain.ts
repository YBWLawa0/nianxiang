export type EnergyScore = 1 | 2 | 3 | 4 | 5

export type GridTag =
  | '工作/事业'
  | '健康/身体'
  | '情感/关系'
  | '财务'
  | '学习/成长'
  | '娱乐/休闲'
  | '家庭'
  | '社交'
  | '其他'

export interface User {
  id: number
  username: string
  created_at: string
}

export interface Note {
  id: number
  content: string
  record_date: string
  energy_score: EnergyScore
  grid_tag: GridTag
  ai_comment: string
  ai_ready: boolean
  created_at: string
}

export interface Diary {
  id: number
  diary_date: string
  title: string
  summary: string
  content: string
  /** 阿响观察（旧接口可能缺省，按空串处理） */
  axiang_observation?: string
  /** 今日一问与收尾鼓励 */
  daily_ritual?: string
  created_at: string
}
