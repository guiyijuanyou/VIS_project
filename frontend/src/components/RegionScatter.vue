<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import type { RegionRow } from '@/api/types'
import { useECharts } from '@/composables/useECharts'
import { axisStyle } from '@/charts/theme'
import { formatCount } from '@/utils/format'
import { useFilterStore } from '@/stores/filter'

/**
 * C03：地区发布量—有效报价中位数散点图。
 * 无有效薪资的地区不放在零薪资位置，单独列出并说明“报价不可用”。
 */
const props = defineProps<{ items: RegionRow[]; selected: string[] }>()
const emit = defineEmits<{ (e: 'toggle', region: string): void }>()

const store = useFilterStore()
const container = ref<HTMLElement | null>(null)
const usable = computed(() => props.items.filter((row) => row.salaryMidMedian !== null))
const unavailable = computed(() => props.items.filter((row) => row.salaryMidMedian === null))

function option(): EChartsOption | null {
  if (usable.value.length === 0) return null
  const rows = usable.value
  return {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const row = rows[params.dataIndex]
        if (!row) return ''
        return [
          `地区：${row.region}`,
          `记录数：${formatCount(row.recordCount)}`,
          `企业数：${formatCount(row.companyCount)}`,
          `有效报价样本：${formatCount(row.salaryValidCount)}`,
          `报价中点中位数：${row.salaryMidMedian} ${row.salaryUnit}`,
        ].join('<br/>')
      },
    },
    xAxis: { ...axisStyle(), type: 'value', name: '记录数', nameLocation: 'middle', nameGap: 28 },
    yAxis: { ...axisStyle(), type: 'value', name: '报价中点中位数', nameGap: 20 },
    series: [
      {
        type: 'scatter',
        data: rows.map((row) => ({
          name: row.region,
          value: [row.recordCount, row.salaryMidMedian as number],
          symbolSize: 8 + Math.sqrt(row.recordCount),
          itemStyle: {
            color: props.selected.includes(row.region) ? '#c0504d' : '#3b6dd8',
            opacity: props.selected.length ? 0.9 : 0.75,
            borderWidth: props.selected.includes(row.region) ? 2 : 0,
            borderColor: '#c0504d',
          },
          label: {
            show: props.selected.includes(row.region),
            position: 'right',
            formatter: row.region,
            fontSize: 10,
          },
        })),
      },
    ],
  }
}

const { chart } = useECharts(container, option)

/**
 * 命中检测放在容器上：按像素找最近的散点，容差 18px。
 * 比依赖 series 的 click 更宽容——小圆点在触控板/投影环境里不容易点中。
 */
function handleCanvasClick(event: MouseEvent) {
  const element = container.value
  const instance = chart.value
  if (!element || !instance) return
  const rect = element.getBoundingClientRect()
  const point = [event.clientX - rect.left, event.clientY - rect.top]
  let nearest: { region: string; distance: number } | null = null
  for (const row of usable.value) {
    const pixel = instance.convertToPixel({ gridIndex: 0 }, [row.recordCount, row.salaryMidMedian as number]) as number[] | string
    if (!Array.isArray(pixel)) continue
    const distance = Math.hypot(pixel[0] - point[0], pixel[1] - point[1])
    if (!nearest || distance < nearest.distance) nearest = { region: row.region, distance }
  }
  if (nearest && nearest.distance <= 18) emit('toggle', nearest.region)
}

onMounted(() => container.value?.addEventListener('click', handleCanvasClick))
onBeforeUnmount(() => container.value?.removeEventListener('click', handleCanvasClick))
</script>

<template>
  <div class="region-scatter">
    <div ref="container" class="region-scatter__canvas"></div>
    <p class="card__hint">
      点击散点选择/取消地区比较对象（最多 4 个，当前 {{ selected.length }} 个）。颜色只表示是否被选中，不表示优劣。
    </p>
    <div v-if="unavailable.length" class="region-scatter__unavailable">
      <strong>报价不可用（{{ unavailable.length }} 个地区）</strong>
      <span>{{ unavailable.map((row) => `${row.region}（${formatCount(row.recordCount)} 条）`).join('、') }}</span>
      <span class="muted">这些地区没有有效薪资样本，因此不落在 0 位置，也不参与薪资比较。</span>
    </div>
    <p v-if="store.meta === null" class="card__hint muted">接口元信息尚未加载，单位以响应字段为准。</p>
  </div>
</template>

<style scoped>
.region-scatter__canvas { width: 100%; height: 320px; }

.region-scatter__unavailable {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  background: var(--color-warning-soft);
  color: var(--color-warning);
  font-size: 12px;
}
</style>
