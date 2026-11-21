import { defineStore } from 'pinia'
import type { Code, Filters, MetaResponse } from '@/api/types'

/**
 * 全站唯一的筛选状态（C02：禁止每张图自己维护不一致条件）。
 * 三页共用；切页保留条件；重置清空。
 */

export function emptyFilters(): Filters {
  return { regions: [], industries: [], jobs: [], educations: [], experiences: [] }
}

export type FilterDimension = keyof Filters

export const useFilterStore = defineStore('filter', {
  state: () => ({
    filters: emptyFilters(),
    /** 地区比较对象（点击散点选择，2～4 个，与全局筛选相互独立） */
    compareRegions: [] as Code[],
    /** 职位差异比较对象（最多 4 个） */
    compareJobs: [] as Code[],
    /** 当前画像的焦点职位 */
    focusJob: '' as Code,
    meta: null as MetaResponse | null,
  }),

  getters: {
    activeCount(state): number {
      const f = state.filters
      return f.regions.length + f.industries.length + f.jobs.length + f.educations.length + f.experiences.length
    },
    /** 条件摘要：页眉与证据页都必须能读到当前条件 */
    summary(state): string {
      const f = state.filters
      const parts: string[] = []
      const push = (name: string, codes: Code[]) => {
        if (codes.length) parts.push(`${name}：${codes.join('、')}`)
      }
      push('地区', f.regions)
      push('行业', f.industries)
      push('职位', f.jobs)
      push('学历', f.educations)
      push('经验', f.experiences)
      return parts.length ? parts.join('；') : '全部数据（无筛选）'
    },
    /** 条件签名：用于 watch 触发重新请求，避免依赖对象引用 */
    queryKey(state): string {
      const f = state.filters
      return JSON.stringify([f.regions, f.industries, f.jobs, f.educations, f.experiences])
    },
    salaryUnit(state): string {
      return state.meta?.salaryUnit ?? 'K/月（单位待接口确认）'
    },
    sampleThreshold(state): number {
      return state.meta?.sampleThreshold ?? 30
    },
    industryOptions(state): Code[] {
      return state.meta?.categories.industries.map((item) => item.code) ?? []
    },
    educationOptions(state): Code[] {
      return state.meta?.categories.educations.map((item) => item.code) ?? []
    },
    experienceOptions(state): Code[] {
      return state.meta?.categories.experiences.map((item) => item.code) ?? []
    },
  },

  actions: {
    setMeta(meta: MetaResponse) {
      this.meta = meta
    },
    isActive(dimension: FilterDimension, code: Code): boolean {
      return this.filters[dimension].includes(code)
    },
    toggle(dimension: FilterDimension, code: Code) {
      const list = this.filters[dimension]
      const index = list.indexOf(code)
      if (index >= 0) list.splice(index, 1)
      else list.push(code)
    },
    clearDimension(dimension: FilterDimension) {
      this.filters[dimension] = []
    },
    resetFilters() {
      this.filters = emptyFilters()
    },
    toggleCompareRegion(code: Code) {
      const index = this.compareRegions.indexOf(code)
      if (index >= 0) {
        this.compareRegions.splice(index, 1)
        return
      }
      if (this.compareRegions.length >= 4) this.compareRegions.shift()
      this.compareRegions.push(code)
    },
    setCompareRegions(codes: Code[]) {
      this.compareRegions = codes.slice(0, 4)
    },
    setFocusJob(code: Code) {
      this.focusJob = code
      if (code && !this.compareJobs.includes(code)) {
        if (this.compareJobs.length >= 4) this.compareJobs.shift()
        this.compareJobs.push(code)
      }
    },
    toggleCompareJob(code: Code) {
      const index = this.compareJobs.indexOf(code)
      if (index >= 0) {
        this.compareJobs.splice(index, 1)
        return
      }
      if (this.compareJobs.length >= 4) this.compareJobs.shift()
      this.compareJobs.push(code)
      if (!this.focusJob) this.focusJob = code
    },
    resetAll() {
      this.filters = emptyFilters()
      this.compareRegions = []
      this.compareJobs = []
      this.focusJob = ''
    },
  },
})
