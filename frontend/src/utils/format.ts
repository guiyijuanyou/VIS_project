/** 数值与代码的统一展示规则：不猜测代码语义，不把 null 显示成 0 */

export function formatCount(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return value.toLocaleString('zh-CN')
}

export function formatPercent(share: number | null | undefined, digits = 1): string {
  if (share === null || share === undefined || Number.isNaN(share)) return '—'
  return `${(share * 100).toFixed(digits)}%`
}

export function formatSalary(value: number | null | undefined, unit: string): string {
  // 无有效报价一律显示“不可用”，不能落成 0（分工第 10 节第 7 条）
  if (value === null || value === undefined || Number.isNaN(value)) return '薪资不可用'
  return `${value} ${unit}`
}

export function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '不可用'
  return Number(value.toFixed(digits)).toString()
}

export function salaryStatusLabel(status: 'ok' | 'invalid' | 'unparsed'): string {
  if (status === 'ok') return '已解析'
  if (status === 'invalid') return '无有效报价'
  return '无法解析'
}

/** 稳定短标签：长代码缩短显示，原代码在悬停时保留（C04） */
export function shortLabel(code: string, max = 10): string {
  return code.length <= max ? code : `${code.slice(0, max - 1)}…`
}
