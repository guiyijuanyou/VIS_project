/**
 * 前端对后端契约的类型声明（人员三 C 维护的类型侧视图）。
 *
 * 契约来源：docs/api/contract.md（人员二 B03 交付，尚未冻结）+ 分工文件第 15 行、第 246～262 行。
 * 分工表里的接口路径是概念示例，这里统一按 协作契约 V1 的 /api/v1/ 前缀实现；
 * 该契约文件目前不在仓库中，因此本文件中的参数命名是**待确认假设**，
 * 记录在 docs/design/request_contract_notes.md，契约定稿后必须同步修改本文件。
 *
 * 强制约定（分工文件第 10 节）：
 * - 发布量与有效薪资量分开计数，无有效薪资返回 null，绝不返回 0。
 * - 代码精确匹配、区分大小写；编码不做语义猜测，界面只展示代码原文。
 */

export type Code = string

export interface CodeOption {
  code: Code
  /** 稳定短标签，仅用于缩短显示，原代码在悬停时保留 */
  label: string
  count?: number
}

/** 全站的筛选条件；同字段多值 OR，不同字段 AND */
export interface Filters {
  regions: Code[]
  industries: Code[]
  jobs: Code[]
  educations: Code[]
  experiences: Code[]
}

export interface MetaResponse {
  dataVersion: string
  apiVersion: string
  /** 薪资单位说明，界面必须原样展示，例如“K / 月（报价中点）” */
  salaryUnit: string
  /** 重复记录口径，界面必须原样展示 */
  duplicatePolicy: string
  quantileMethod: string
  /** 低于该样本数的对象从主排名剔除（项目展示阈值，非统计显著性） */
  sampleThreshold: number
  /** true 表示当前由前端模拟数据供数，界面必须显示模拟标记 */
  mock: boolean
  categories: {
    industries: CodeOption[]
    educations: CodeOption[]
    experiences: CodeOption[]
  }
}

export interface OverviewResponse {
  recordCount: number
  companyCount: number
  regionCount: number
  jobCount: number
  salaryValidCount: number
  salaryValidRate: number
  /** 有效报价中点中位数；无有效样本时为 null */
  salaryMidMedian: number | null
  salaryUnit: string
}

export interface JobOption {
  code: Code
  label: string
  recordCount: number
}

export interface JobOptionsResponse {
  items: JobOption[]
  page: number
  pageSize: number
  total: number
}

export interface ShareItem {
  code: Code
  label: string
  count: number
  /** 占比，分母为该对象在筛选条件下的记录数 */
  share: number
}

export interface RegionRow {
  region: Code
  label: string
  recordCount: number
  companyCount: number
  salaryValidCount: number
  /** 有效报价中点中位数；无有效样本时为 null（界面显示“不可用”，不落在 0 位） */
  salaryMidMedian: number | null
  salaryUnit: string
  /** 该地区占比最高的行业，仅作对照，不参与区域结构评述 */
  topIndustry: Code | null
  /**
   * 行业占比向量 + 有效报价分位摘要：C03“选 2～4 个地区比较行业占比与薪资分布”必需。
   * 契约（docs/api/contract.md）尚未冻结，字段名是前端提出的需求，
   * 缺失时界面显示“接口未提供”，不会自行推算替代值。
   */
  industryShare?: ShareItem[]
  salary?: SalarySummary | null
}

export interface RegionsResponse {
  items: RegionRow[]
  salaryUnit: string
  /** 该响应的筛选条件快照，便于界面核对条件一致性 */
  filters: Filters
}

export interface SalarySummary {
  p05: number
  p25: number
  p50: number
  p75: number
  p95: number
  min: number
  max: number
  sampleCount: number
  unit: string
}

export interface JobProfileResponse {
  job: Code
  label: string
  recordCount: number
  companyCount: number
  regionCount: number
  salaryValidCount: number
  salary: SalarySummary | null
  /** 三个类别维度的分布；分母固定为 recordCount，缺失与未知一致处理 */
  categories: {
    dimension: 'industry' | 'education' | 'experience'
    items: ShareItem[]
  }[]
  /** 各经验代码下的有效报价中位数（对照用，样本不足处为 null） */
  salaryByExperience: { code: Code; label: string; sampleCount: number; median: number | null }[]
}

export type DistanceDimension = 'industry' | 'region' | 'education' | 'experience' | 'salary'

export interface DistanceComponent {
  dimension: DistanceDimension
  /** 该维距离 0～1；维度不可用（如缺少有效薪资）时为 null */
  value: number | null
  note: string
}

export interface JobDistanceResponse {
  jobs: Code[]
  labels: Record<Code, string>
  /** 算法版本与参考集合必须随结果返回（分工第 10 节第 6 条） */
  algorithmVersion: string
  referenceSet: string
  dimensions: DistanceDimension[]
  /** 对称矩阵，对角线为 0；任一维度不参与时为 null */
  matrix: (number | null)[][]
  /** 每一对的各维分量，键为 "A|B"，让界面能解释“为什么不同” */
  components: Record<string, DistanceComponent[]>
  warnings: string[]
}

export interface SimilarRegionItem {
  region: Code
  label: string
  similarity: number
  recordCount: number
  topIndustry: Code | null
}

export interface SimilarRegionsResponse {
  region: Code
  method: string
  reference: string
  items: SimilarRegionItem[]
}

export type SalaryStatus = 'ok' | 'invalid' | 'unparsed'

export interface JobRecord {
  recordId: string
  sourceRow: number
  jobTitle: Code
  city: Code
  salary: string
  experience: Code
  education: Code
  company: Code
  companyType: Code
  salaryLower: number | null
  salaryUpper: number | null
  salaryMid: number | null
  salaryUnit: string | null
  payMonths: number | null
  salaryStatus: SalaryStatus
  isExtraDuplicate: boolean
}

export interface RecordsResponse {
  items: JobRecord[]
  page: number
  pageSize: number
  total: number
  filters: Filters
}
