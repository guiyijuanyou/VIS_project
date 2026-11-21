import type { EChartsOption } from 'echarts'

/** 全站一致的颜色编码（类别色顺序固定，三页同一类别同色） */
export const PALETTE = [
  '#3b6dd8',
  '#e0803a',
  '#3a9e8f',
  '#c0504d',
  '#7d6bc4',
  '#b3a01e',
  '#4a8fc7',
  '#c96fa0',
  '#5b9e4c',
  '#8a7f6d',
  '#2f7fa8',
  '#a75f3c',
]

export const AXIS_COLOR = '#8a94a6'
export const GRID_COLOR = '#e8ebf2'
export const TEXT_COLOR = '#2b3242'

/** 统一的基础样式，避免 8 个组件各写一套字体/网格/提示框 */
export function applyChartTheme(option: EChartsOption): EChartsOption {
  return {
    color: PALETTE,
    textStyle: { color: TEXT_COLOR, fontFamily: 'inherit', fontSize: 12 },
    grid: { left: 56, right: 24, top: 40, bottom: 48, containLabel: true },
    tooltip: { confine: true, textStyle: { fontSize: 12 } },
    ...option,
  }
}

/**
 * 坐标轴公共样式。使用方式固定为「先展开，再写字面量覆盖」：
 *   { ...axisStyle(), type: 'value', name: '记录数' }
 */
export function axisStyle() {
  return {
    nameTextStyle: { color: AXIS_COLOR },
    axisLine: { lineStyle: { color: GRID_COLOR } },
    axisLabel: { color: AXIS_COLOR },
    splitLine: { lineStyle: { color: GRID_COLOR } },
  }
}
