<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import type { RegionRow } from '@/api/types'
import { useECharts } from '@/composables/useECharts'
import { axisStyle, BRAND, BRAND_ACCENT } from '@/charts/theme'
import { formatCount } from '@/utils/format'
import { useFilterStore } from '@/stores/filter'
import Tag from './Tag.vue'

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
    series: [
      {
        type: 'scatter',
        data: rows.map((row) => ({
          name: row.region,
          value: [row.recordCount, row.salaryMidMedian as number],
          symbolSize: 7 + Math.sqrt(row.recordCount) * 0.9,
          itemStyle: {
            color: props.selected.includes(row.region) ? BRAND_ACCENT : BRAND,
            opacity: props.selected.length && !props.selected.includes(row.region) ? 0.45 : 0.85,
            borderWidth: props.selected.includes(row.region) ? 1.5 : 0,
            borderColor: BRAND_ACCENT,
          },
          label: {
            show: props.selected.includes(row.region),
            position: 'right',
            formatter: row.region,
            fontSize: 10,
            color: BRAND_ACCENT,
          },
        })),
      },
    ],
    xAxis: { ...axisStyle(), type: 'value', name: '记录数', nameLocation: 'middle', nameGap: 26 },
    yAxis: { ...axisStyle(), type: 'value', name: '报价中点中位数', nameGap: 14 },
  }
}

const { chart } = useECharts(container, option)

/** 命中检测放在容器上：按像素找最近的散点，容差 18px，避免小圆点难以点中 */
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
  <div class="scatter">
    <div ref="container" class="scatter__canvas"></div>
    <p class="chart-note">
      点宽表示记录数；点击圆点选择或取消地区比较对象（当前 {{ selected.length }} / 4）。颜色只表示是否被选中，不表示优劣。
    </p>
    <div v-if="unavailable.length" class="scatter__unavailable">
      <div class="scatter__unavailable-head">
        <Tag tone="warning">报价不可用</Tag>
        <span class="scatter__unavailable-count num">{{ unavailable.length }} 个地区</span>
      </div>
      <div class="scatter__tags">
        <Tag v-for="row in unavailable" :key="row.region" :title="`${row.region}：${formatCount(row.recordCount)} 条记录`">
          {{ row.region }} · {{ formatCount(row.recordCount) }}
        </Tag>
      </div>
      <p class="chart-note">这些地区没有有效薪资样本，因此不落在 0 位置，也不参与薪资比较。</p>
    </div>
    <p v-if="store.meta === null" class="chart-note">接口元信息尚未加载，单位以响应字段为准。</p>
  </div>
</template>

<style scoped>
.scatter__canvas {
  width: 100%;
  height: 300px;
}

.scatter__unavailable {
  margin-top: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid #e8d9bf;
  border-radius: var(--radius-sm);
  background: var(--color-warning-soft);
}

.scatter__unavailable-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.scatter__unavailable-count {
  font-size: var(--text-xs);
  color: var(--color-warning);
}

.scatter__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-top: var(--space-2);
}
</style>
