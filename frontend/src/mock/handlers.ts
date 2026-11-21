import type {
  DistanceComponent,
  DistanceDimension,
  Filters,
  JobDistanceResponse,
  JobOptionsResponse,
  JobProfileResponse,
  JobRecord,
  MetaResponse,
  OverviewResponse,
  RegionRow,
  RegionsResponse,
  RecordsResponse,
  SalarySummary,
  ShareItem,
  SimilarRegionsResponse,
  Code,
} from '@/api/types'
import { ApiError, type QueryParams } from '@/api/client'
import { mockDataset } from './dataset'

/**
 * ⚠️ 模拟响应（SIMULATED）—— 与 src/api/types.ts 的结构一致，供界面在 H3 之前开发。
 *
 * 这里只是把 mock 记录临时聚合出来，**不是**人员一/人员二的统计口径：
 * 分位数方法、重复口径、采样阈值等一律以 docs/api/contract.md 与 docs/data/metrics.md 为准。
 * real 模式下本文件不会被调用。
 */

const DATA_VERSION = 'mock-2024-11-18'
const SALARY_UNIT = 'K/月（报价中点，模拟）'
const SAMPLE_THRESHOLD = 30

function median(values: number[]): number | null {
  if (values.length === 0) return null
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  const value = sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
  return Number(value.toFixed(2))
}

function quantile(sorted: number[], q: number): number {
  if (sorted.length === 0) return Number.NaN
  const position = (sorted.length - 1) * q
  const base = Math.floor(position)
  const rest = position - base
  const next = sorted[Math.min(base + 1, sorted.length - 1)]
  return Number((sorted[base] + rest * (next - sorted[base])).toFixed(2))
}

function asArray(params: QueryParams, key: string): string[] {
  const raw = params?.[key]
  if (raw === undefined || raw === null) return []
  if (Array.isArray(raw)) return raw.filter((item) => item !== '')
  if (typeof raw === 'string' && raw !== '') return raw.split(',').filter((item) => item !== '')
  return []
}

function readFilters(params: QueryParams): Filters {
  return {
    regions: asArray(params, 'region'),
    industries: asArray(params, 'industry'),
    jobs: asArray(params, 'job'),
    educations: asArray(params, 'education'),
    experiences: asArray(params, 'experience'),
  }
}

function applyFilters(records: JobRecord[], filters: Filters): JobRecord[] {
  return records.filter((record) => {
    if (filters.regions.length && !filters.regions.includes(record.city)) return false
    if (filters.industries.length && !filters.industries.includes(record.companyType)) return false
    if (filters.jobs.length && !filters.jobs.includes(record.jobTitle)) return false
    if (filters.educations.length && !filters.educations.includes(record.education)) return false
    if (filters.experiences.length && !filters.experiences.includes(record.experience)) return false
    return true
  })
}

function labelsFor(codes: string[]): Map<Code, string> {
  // mock 阶段不做任何代码到语义标签的映射（分工第 1.1 节），标签即代码
  return new Map(codes.map((code) => [code, code]))
}

function shareItems(records: JobRecord[], dimension: 'industry' | 'education' | 'experience', codes: string[]): ShareItem[] {
  const counter = new Map<string, number>()
  for (const record of records) {
    const code = dimension === 'industry' ? record.companyType : dimension === 'education' ? record.education : record.experience
    counter.set(code, (counter.get(code) ?? 0) + 1)
  }
  const labels = labelsFor(codes)
  const total = records.length
  return [...counter.entries()]
    .map(([code, count]) => ({ code, label: labels.get(code) ?? code, count, share: total ? count / total : 0 }))
    .sort((a, b) => b.count - a.count)
}

function topIndustry(records: JobRecord[]): Code | null {
  const items = shareItems(records, 'industry', mockDataset.industries)
  return items.length ? items[0].code : null
}

function meta(): MetaResponse {
  const label = (code: string) => ({ code, label: code })
  return {
    dataVersion: DATA_VERSION,
    apiVersion: 'mock',
    salaryUnit: SALARY_UNIT,
    duplicatePolicy: '默认保留全部原始记录并标记额外重复（模拟）',
    quantileMethod: '线性插值 p05/p25/p50/p75/p95（模拟，未与人员一对照）',
    sampleThreshold: SAMPLE_THRESHOLD,
    mock: true,
    categories: {
      industries: mockDataset.industries.map(label),
      educations: mockDataset.educations.map(label),
      experiences: mockDataset.experiences.map(label),
    },
  }
}

function overview(filters: Filters): OverviewResponse {
  const records = applyFilters(mockDataset.records, filters)
  const salaryValues = records.map((r) => r.salaryMid).filter((v): v is number => v !== null)
  return {
    recordCount: records.length,
    companyCount: new Set(records.map((r) => r.company)).size,
    regionCount: new Set(records.map((r) => r.city)).size,
    jobCount: new Set(records.map((r) => r.jobTitle)).size,
    salaryValidCount: salaryValues.length,
    salaryValidRate: records.length ? salaryValues.length / records.length : 0,
    salaryMidMedian: median(salaryValues),
    salaryUnit: SALARY_UNIT,
  }
}

function jobOptions(params: QueryParams): JobOptionsResponse {
  const keyword = String(params?.q ?? '').trim()
  const page = Math.max(1, Number(params?.page ?? 1))
  const pageSize = Math.min(50, Math.max(1, Number(params?.pageSize ?? 20)))
  const counts = new Map<string, number>()
  for (const record of mockDataset.records) counts.set(record.jobTitle, (counts.get(record.jobTitle) ?? 0) + 1)
  const all = [...counts.entries()]
    .map(([code, count]) => ({ code, label: code, recordCount: count }))
    .filter((item) => (keyword ? item.code.includes(keyword) : true))
    .sort((a, b) => b.recordCount - a.recordCount || a.code.localeCompare(b.code))
  const start = (page - 1) * pageSize
  return { items: all.slice(start, start + pageSize), page, pageSize, total: all.length }
}

function regions(params: QueryParams): RegionsResponse {
  const filters = readFilters(params)
  const records = applyFilters(mockDataset.records, filters)
  const byRegion = new Map<string, JobRecord[]>()
  for (const record of records) {
    const list = byRegion.get(record.city) ?? []
    list.push(record)
    byRegion.set(record.city, list)
  }
  const items: RegionRow[] = mockDataset.regions
    .map((region) => {
      const group = byRegion.get(region) ?? []
      const salaryValues = group.map((r) => r.salaryMid).filter((v): v is number => v !== null)
      return {
        region,
        label: region,
        recordCount: group.length,
        companyCount: new Set(group.map((r) => r.company)).size,
        salaryValidCount: salaryValues.length,
        salaryMidMedian: median(salaryValues),
        salaryUnit: SALARY_UNIT,
        topIndustry: topIndustry(group),
        industryShare: shareItems(group, 'industry', mockDataset.industries).slice(0, 6),
        salary: salarySummary(group),
      }
    })
    .filter((row) => row.recordCount > 0)
    .sort((a, b) => b.recordCount - a.recordCount)
  return { items, salaryUnit: SALARY_UNIT, filters }
}

function salarySummary(records: JobRecord[]): SalarySummary | null {
  const values = records.map((r) => r.salaryMid).filter((v): v is number => v !== null)
  if (values.length === 0) return null
  const sorted = [...values].sort((a, b) => a - b)
  return {
    p05: quantile(sorted, 0.05),
    p25: quantile(sorted, 0.25),
    p50: quantile(sorted, 0.5),
    p75: quantile(sorted, 0.75),
    p95: quantile(sorted, 0.95),
    min: sorted[0],
    max: sorted[sorted.length - 1],
    sampleCount: sorted.length,
    unit: SALARY_UNIT,
  }
}

function jobProfile(params: QueryParams): JobProfileResponse {
  const filters = readFilters(params)
  const job = filters.jobs[0] ?? String(params?.job ?? '')
  if (!job) throw new ApiError(400, 'MISSING_JOB', '缺少 job 参数')
  const records = applyFilters(mockDataset.records, { ...filters, jobs: [job] })
  const byExperience = new Map<string, number[]>()
  for (const record of records) {
    if (record.salaryMid === null) continue
    const list = byExperience.get(record.experience) ?? []
    list.push(record.salaryMid)
    byExperience.set(record.experience, list)
  }
  return {
    job,
    label: job,
    recordCount: records.length,
    companyCount: new Set(records.map((r) => r.company)).size,
    regionCount: new Set(records.map((r) => r.city)).size,
    salaryValidCount: records.filter((r) => r.salaryStatus === 'ok').length,
    salary: salarySummary(records),
    categories: [
      { dimension: 'industry', items: shareItems(records, 'industry', mockDataset.industries) },
      { dimension: 'education', items: shareItems(records, 'education', mockDataset.educations) },
      { dimension: 'experience', items: shareItems(records, 'experience', mockDataset.experiences) },
    ],
    salaryByExperience: [...byExperience.entries()]
      .map(([code, values]) => ({ code, label: code, sampleCount: values.length, median: median(values) }))
      .sort((a, b) => a.code.localeCompare(b.code)),
  }
}

function proportion(records: JobRecord[], pick: (record: JobRecord) => string, codes: string[]): Map<string, number> {
  const map = new Map<string, number>(codes.map((code) => [code, 0]))
  for (const record of records) {
    const code = pick(record)
    map.set(code, (map.get(code) ?? 0) + 1)
  }
  const total = records.length || 1
  for (const [code, count] of map) map.set(code, count / total)
  return map
}

function totalVariation(a: Map<string, number>, b: Map<string, number>): number {
  let sum = 0
  for (const key of new Set([...a.keys(), ...b.keys()])) sum += Math.abs((a.get(key) ?? 0) - (b.get(key) ?? 0))
  return Math.min(1, sum / 2)
}

function jobDistance(params: QueryParams): JobDistanceResponse {
  const filters = readFilters(params)
  const jobs = asArray(params, 'job')
  const selected = (jobs.length ? jobs : filters.jobs).slice(0, 4)
  if (selected.length < 2) throw new ApiError(400, 'NEED_TWO_JOBS', '差异度至少需要两个职位')
  const groups = new Map<Code, JobRecord[]>(selected.map((job) => [job, applyFilters(mockDataset.records, { ...filters, jobs: [job] })]))
  const medians = new Map<Code, number | null>(selected.map((job) => [job, median((groups.get(job) ?? []).map((r) => r.salaryMid).filter((v): v is number => v !== null))]))
  const availableMedians = [...medians.values()].filter((v): v is number => v !== null).sort((a, b) => a - b)
  const reference = availableMedians.length >= 2
    ? Math.max(1e-6, quantile(availableMedians, 0.95) - quantile(availableMedians, 0.05))
    : 1

  const vectorOf = (records: JobRecord[], dimension: DistanceDimension): Map<string, number> => {
    if (dimension === 'industry') return proportion(records, (r) => r.companyType, mockDataset.industries)
    if (dimension === 'region') return proportion(records, (r) => r.city, mockDataset.regions)
    if (dimension === 'education') return proportion(records, (r) => r.education, mockDataset.educations)
    return proportion(records, (r) => r.experience, mockDataset.experiences)
  }

  const dimensions: DistanceDimension[] = ['industry', 'region', 'education', 'experience', 'salary']
  const matrix: (number | null)[][] = selected.map(() => selected.map(() => null))
  const components: Record<string, DistanceComponent[]> = {}
  const warnings: string[] = []

  selected.forEach((jobA, i) => {
    matrix[i][i] = 0
    for (let j = i + 1; j < selected.length; j += 1) {
      const jobB = selected[j]
      const parts: DistanceComponent[] = []
      for (const dimension of dimensions) {
        if (dimension === 'salary') {
          const a = medians.get(jobA) ?? null
          const b = medians.get(jobB) ?? null
          if (a === null || b === null) {
            parts.push({ dimension, value: null, note: '缺少有效薪资，不参与等权平均' })
          } else {
            parts.push({ dimension, value: Math.min(1, Math.abs(a - b) / reference), note: `中位数差 ${Math.abs(a - b).toFixed(2)} / 参考范围 ${reference.toFixed(2)}` })
          }
          continue
        }
        parts.push({ dimension, value: totalVariation(vectorOf(groups.get(jobA) ?? [], dimension), vectorOf(groups.get(jobB) ?? [], dimension)), note: '总变差 TV = 0.5 * Σ|p-q|' })
      }
      const usable = parts.filter((p): p is DistanceComponent & { value: number } => p.value !== null)
      const score = usable.reduce((sum, p) => sum + p.value, 0) / usable.length
      matrix[i][j] = Number(score.toFixed(4))
      matrix[j][i] = matrix[i][j]
      const key = `${jobA}|${jobB}`
      components[key] = parts
      components[`${jobB}|${jobA}`] = parts
      if (usable.length < dimensions.length) warnings.push(`${key} 仅使用 ${usable.length}/${dimensions.length} 个维度，未参与维度已标记`)
    }
  })
  if (warnings.length === 0) warnings.push('所有维度均可用，差异度为等权平均（分析设计，不是事实规律）')

  return {
    jobs: selected,
    labels: Object.fromEntries(labelsFor(selected)),
    algorithmVersion: 'mock-tv-v0（不参与交付口径）',
    referenceSet: '当前筛选条件下的模拟记录',
    dimensions,
    matrix,
    components,
    warnings,
  }
}

function similarRegions(params: QueryParams): SimilarRegionsResponse {
  const region = String(params?.region ?? '')
  if (!region) throw new ApiError(400, 'MISSING_REGION', '缺少 region 参数')
  // 相似度固定使用全量数据（不随筛选变化），界面上必须如实标注（分工第 10 节第 6 条）
  const globalRecords = mockDataset.records
  const target = proportion(globalRecords.filter((r) => r.city === region), (r) => r.companyType, mockDataset.industries)
  const items = mockDataset.regions
    .filter((code) => code !== region)
    .map((code) => {
      const group = globalRecords.filter((r) => r.city === code)
      const vector = proportion(group, (r) => r.companyType, mockDataset.industries)
      return {
        region: code,
        label: code,
        similarity: Number((1 - totalVariation(target, vector)).toFixed(4)),
        recordCount: group.length,
        topIndustry: topIndustry(group),
      }
    })
    .filter((item) => item.recordCount > 0)
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, 5)
  return {
    region,
    method: '1 - TV(行业结构占比)（模拟）',
    reference: '全局行业发布结构快照，不随页面筛选重算',
    items,
  }
}

function recordsPage(params: QueryParams): RecordsResponse {
  const filters = readFilters(params)
  const page = Math.max(1, Number(params?.page ?? 1))
  const pageSize = Math.min(100, Math.max(1, Number(params?.pageSize ?? 20)))
  const filtered = applyFilters(mockDataset.records, filters)
    .slice()
    .sort((a, b) => a.sourceRow - b.sourceRow)
  const start = (page - 1) * pageSize
  return { items: filtered.slice(start, start + pageSize), page, pageSize, total: filtered.length, filters }
}

function delay(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException('Aborted', 'AbortError'))
      return
    }
    const timer = setTimeout(() => {
      signal?.removeEventListener('abort', onAbort)
      resolve()
    }, ms)
    const onAbort = () => {
      clearTimeout(timer)
      reject(new DOMException('Aborted', 'AbortError'))
    }
    signal?.addEventListener('abort', onAbort, { once: true })
  })
}

const routes: Record<string, (params: QueryParams) => unknown> = {
  '/meta': () => meta(),
  '/options/jobs': jobOptions,
  '/overview': (params) => overview(readFilters(params)),
  '/regions': regions,
  '/jobs/profile': jobProfile,
  '/jobs/distance': jobDistance,
  '/regions/similar': similarRegions,
  '/records': recordsPage,
}

export async function handleMockRequest<T>(path: string, params?: QueryParams, signal?: AbortSignal): Promise<T> {
  const handler = routes[path]
  if (!handler) throw new ApiError(404, 'MOCK_NOT_FOUND', `模拟数据未定义接口：${path}`)
  await delay(120, signal)
  return handler(params ?? {}) as T
}
