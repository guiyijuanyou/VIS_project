import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { onBeforeUnmount, onMounted, watch, shallowRef, type Ref } from 'vue'
import { applyChartTheme } from '@/charts/theme'

/** 图表容器生命周期统一封装：初始化、尺寸监听、销毁，避免每个组件重复处理 */
export function useECharts(
  container: Ref<HTMLElement | null>,
  option: () => EChartsOption | null,
  onInit?: (chart: echarts.ECharts) => void,
) {
  const chart = shallowRef<echarts.ECharts | null>(null)
  let observer: ResizeObserver | null = null

  function render() {
    const next = option()
    if (!next || !chart.value) return
    chart.value.setOption(applyChartTheme(next), true)
  }

  onMounted(() => {
    if (!container.value) return
    chart.value = echarts.init(container.value, undefined, { renderer: 'canvas' })
    if (onInit) onInit(chart.value)
    render()
    observer = new ResizeObserver(() => chart.value?.resize())
    observer.observe(container.value)
  })

  watch(option, render)

  onBeforeUnmount(() => {
    observer?.disconnect()
    observer = null
    chart.value?.dispose()
    chart.value = null
  })

  return { chart, render }
}
