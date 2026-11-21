import type { JobRecord, SalaryStatus } from '@/api/types'

/**
 * ⚠️ 模拟数据（SIMULATED）—— 不是真实统计结果，仅用于人员三 H3 之前的界面开发。
 *
 * 生成方式：固定随机种子 + 本项目自造的代码体系（R/I/E/X/P 前缀），
 * 与 ChinaVis 2024 虚拟招聘数据的真实代码没有任何对应关系。
 * 人员一的清洗规则（config/cleaning_rules.json、A02）与人员二的真实接口（H3）就绪后，
 * 把 VITE_API_MODE 改为 real 即可整体替换；本目录不会被真实接口复用。
 *
 * 数值可复现：同一份代码在任何机器上都生成同样的 800 条记录。
 */

export interface MockDataset {
  regions: string[]
  industries: string[]
  educations: string[]
  experiences: string[]
  jobs: string[]
  records: JobRecord[]
}

const SEED = 20241118
const RECORD_COUNT = 800

function mulberry32(seed: number): () => number {
  let a = seed
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function pad(prefix: string, index: number, width: number): string {
  return prefix + String(index).padStart(width, '0')
}

interface ParsedSalary {
  lower: number | null
  upper: number | null
  mid: number | null
  unit: string | null
  payMonths: number | null
  status: SalaryStatus
}

/** 仅用于让模拟数据内部自洽；真实解析规则属于人员一 A02，本函数不可作为口径依据 */
export function parseMockSalary(raw: string): ParsedSalary {
  const interval = /^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)K(?:·(\d+)薪)?$/.exec(raw)
  if (interval) {
    const lower = Number(interval[1])
    const upper = Number(interval[2])
    return {
      lower,
      upper,
      mid: Number(((lower + upper) / 2).toFixed(2)),
      unit: 'K/月',
      payMonths: interval[3] ? Number(interval[3]) : null,
      status: 'ok',
    }
  }
  const single = /^(\d+(?:\.\d+)?)K$/.exec(raw)
  if (single) {
    const value = Number(single[1])
    return { lower: value, upper: value, mid: value, unit: 'K/月', payMonths: null, status: 'ok' }
  }
  if (raw === '面议') return { lower: null, upper: null, mid: null, unit: null, payMonths: null, status: 'invalid' }
  return { lower: null, upper: null, mid: null, unit: null, payMonths: null, status: 'unparsed' }
}

function makeSalaryText(rng: () => number): string {
  const roll = rng()
  const lower = 4 + Math.floor(rng() * 26)
  const upper = lower + 2 + Math.floor(rng() * 18)
  if (roll < 0.7) return `${lower}-${upper}K`
  if (roll < 0.85) return `${lower}-${upper}K·${13 + Math.floor(rng() * 3)}薪`
  if (roll < 0.92) return `${lower}K`
  if (roll < 0.97) return '面议'
  return `${lower}-${upper}K以上`
}

function weightedPick(rng: () => number, codes: string[], weights: number[]): string {
  const total = weights.reduce((sum, w) => sum + w, 0)
  let target = rng() * total
  for (let i = 0; i < codes.length; i += 1) {
    target -= weights[i]
    if (target <= 0) return codes[i]
  }
  return codes[codes.length - 1]
}

export function buildMockDataset(): MockDataset {
  const rng = mulberry32(SEED)
  const regions = Array.from({ length: 24 }, (_, i) => pad('R', i + 1, 3))
  const industries = Array.from({ length: 12 }, (_, i) => pad('I', i + 1, 2))
  const educations = Array.from({ length: 12 }, (_, i) => pad('E', i + 1, 2))
  const experiences = Array.from({ length: 10 }, (_, i) => pad('X', i + 1, 2))
  const jobs = Array.from({ length: 20 }, (_, i) => pad('P', i + 1, 3))

  const regionWeights = regions.map((_, i) => 1 + (i % 6) * 1.8)
  const jobWeights = jobs.map((_, i) => 1 + (i % 5) * 2.4)
  const industryWeights = industries.map((_, i) => 1 + (i % 4) * 1.5)

  const records: JobRecord[] = []
  for (let i = 0; i < RECORD_COUNT; i += 1) {
    const city = weightedPick(rng, regions, regionWeights)
    const jobTitle = weightedPick(rng, jobs, jobWeights)
    const companyType = weightedPick(rng, industries, industryWeights)
    const experience = experiences[Math.floor(rng() * experiences.length)]
    const education = educations[Math.floor(rng() * educations.length)]
    const companyIndex = 1 + Math.floor(rng() * 150)
    const raw = makeSalaryText(rng)
    const parsed = parseMockSalary(raw)
    records.push({
      recordId: `MOCK-${String(i + 1).padStart(5, '0')}`,
      sourceRow: i + 2,
      jobTitle,
      city,
      salary: raw,
      experience,
      education,
      company: pad('C', companyIndex, 4),
      companyType,
      salaryLower: parsed.lower,
      salaryUpper: parsed.upper,
      salaryMid: parsed.mid,
      salaryUnit: parsed.unit,
      payMonths: parsed.payMonths,
      salaryStatus: parsed.status,
      // 与真实数据一致：重复记录默认保留并标记（分工第 10 节第 1 条）
      isExtraDuplicate: i % 97 === 0,
    })
  }

  return { regions, industries, educations, experiences, jobs, records }
}

export const mockDataset: MockDataset = buildMockDataset()
