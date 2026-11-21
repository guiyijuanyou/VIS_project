import type { EChartsOption } from 'echarts'

/**
 * 图表视觉规范：颜色服务于数据分类，不追求视觉丰富。
 * 取值与 styles/tokens.css 保持一致（canvas 无法解析 CSS 变量，故在此登记同值常量）。
 */

/** 主品牌色：用于单一强调与主要序列 */
export const BRAND = '#294c69'
/** 深色强调：用于选中等强对比状态 */
export const BRAND_ACCENT = '#c45b52'
/** 警示色：仅用于“样本不足/需注意”的单点标记 */
export const WARNING_POINT = '#c28a3c'
/** 次要中性色：不作为主题色使用，仅用于网格与坐标 */
export const AXIS_COLOR = '#929ba6'
export const GRID_COLOR = '#e2e6ea'
export const TEXT_COLOR = '#202a35'

/** 低饱和度分类色板：同一类别在全站保持同色 */
export const PALETTE = [
  '#294c69',
  '#5a86a8',
  '#27836a',
  '#c28a3c',
  '#c45b52',
  '#6b8299',
  '#8c9aa6',
  '#1d354a',
  '#6f9c8b',
  '#a8814a',
  '#9c6b64',
  '#7e8b99',
]

const TOOLTIP_DEFAULTS = {
  backgroundColor: '#ffffff',
  borderColor: '#e2e6ea',
  borderWidth: 1,
  padding: 8,
  textStyle: { color: TEXT_COLOR, fontSize: 12, lineHeight: 18 },
  extraCssText: 'box-shadow: 0 4px 16px rgba(32,42,53,0.12); border-radius: 4px;',
}

const LEGEND_DEFAULTS = {
  top: 0,
  right: 0,
  icon: 'rect',
  itemWidth: 8,
  itemHeight: 8,
  itemGap: 12,
  textStyle: { color: '#697586', fontSize: 11 },
}

const GRID_DEFAULTS = { left: 12, right: 16, top: 36, bottom: 8, containLabel: true }

/** 统一基础样式：字体、色板、提示框、图例与网格留白 */
export function applyChartTheme(option: EChartsOption): EChartsOption {
  const tooltip = Array.isArray(option.tooltip) ? option.tooltip[0] : option.tooltip
  const legend = Array.isArray(option.legend) ? option.legend[0] : option.legend
  return {
    color: PALETTE,
    textStyle: { color: TEXT_COLOR, fontFamily: 'inherit', fontSize: 11 },
    ...option,
    grid: { ...GRID_DEFAULTS, ...(option.grid as object | undefined) },
    tooltip: { ...TOOLTIP_DEFAULTS, ...(tooltip as object | undefined) } as EChartsOption['tooltip'],
    legend: { ...LEGEND_DEFAULTS, ...(legend as object | undefined) } as EChartsOption['legend'],
  }
}

/**
 * 坐标轴公共样式。使用方式固定为「先展开，再写字面量覆盖」：
 *   { ...axisStyle(), type: 'value', name: '记录数' }
 */
export function axisStyle() {
  return {
    nameTextStyle: { color: AXIS_COLOR, fontSize: 11 },
    axisLine: { lineStyle: { color: GRID_COLOR } },
    axisTick: { show: false },
    axisLabel: { color: AXIS_COLOR, fontSize: 11 },
    splitLine: { lineStyle: { color: GRID_COLOR } },
  }
}
