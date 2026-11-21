<script setup lang="ts">
import { computed, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import type { RegionRow } from '@/api/types'
import { useECharts } from '@/composables/useECharts'
import { AXIS_COLOR, axisStyle } from '@/charts/theme'
import { formatCount, formatNumber } from '@/utils/format'
import Tag from './Tag.vue'
import DataTable from './DataTable.vue'
import type { DataTableColumn } from './table-types'
import EmptyState from './EmptyState.vue'

/** C03：2～4 个地区的行业占比与薪资分布比较；缺失字段如实提示，不自行推算 */
const props = defineProps<{ items: RegionRow[]; selected: string[] }>()
const emit = defineEmits<{ (e: 'remove', region: string): void }>()

const container = ref<HTMLElement | null>(null)
const compared = computed(() => props.items.filter((row) => props.selected.includes(row.region)))
const hasShare = computed(() => compared.value.some((row) => (row.industryShare?.length ?? 0) > 0))

const industryCodes = computed(() => {
  const codes = new Set<string>()
  for (const row of compared.value) for (const item of row.industryShare ?? []) codes.add(item.code)
  return [...codes]
})

function option(): EChartsOption | null {
  if (compared.value.length === 0 || !hasShare.value) return null
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: any) => `${(Number(value) * 100).toFixed(1)}%` },
    legend: {},
    series: compared.value.map((row) => ({
      name: row.region,
      type: 'bar',
      data: industryCodes.value.map((code) => row.industryShare?.find((item) => item.code === code)?.share ?? 0),
      barMaxWidth: 20,
    })),
    xAxis: { ...axisStyle(), type: 'category', data: industryCodes.value, splitLine: { show: false } },
    yAxis: {
      ...axisStyle(),
      type: 'value',
      name: '地区内占比',
      axisLabel: { color: AXIS_COLOR, fontSize: 11, formatter: (value: number) => `${(value * 100).toFixed(0)}%` },
    },
  }
}

useECharts(container, option)

const columns: DataTableColumn[] = [
  { key: 'region', label: '地区', width: '84px' },
  { key: 'recordCount', label: '记录数', align: 'right', width: '80px' },
  { key: 'companyCount', label: '企业数', align: 'right', width: '76px' },
  { key: 'salaryValidCount', label: '有效报价样本', align: 'right', width: '108px' },
  { key: 'median', label: '报价中位数', align: 'right', width: '132px' },
  { key: 'quartiles', label: 'P25 ～ P75', align: 'right', width: '132px' },
  { key: 'topIndustry', label: '占比最高行业', width: '112px' },
]

const rows = computed(() => compared.value)
</script>

<template>
  <div>
    <EmptyState v-if="compared.length === 0" title="尚未选择比较地区" hint="在上方散点图中点选 2～4 个地区。" />
    <template v-else>
      <div class="compare__bar">
        <div class="compare__tags">
          <Tag v-for="row in compared" :key="row.region" tone="brand" removable @remove="emit('remove', row.region)">
            {{ row.region }}
          </Tag>
        </div>
        <span class="compare__scale">分母：各地区在当前筛选条件下的记录数</span>
      </div>

      <div v-if="hasShare" ref="container" class="compare__canvas"></div>
      <EmptyState
        v-else
        title="接口未返回地区行业占比"
        hint="缺少 industryShare 字段，无法绘制结构比较；需在 docs/api/contract.md 中确认该字段。"
      />

      <DataTable :columns="columns" :rows="rows" :row-key="(row) => row.region">
        <template #cell="{ row, column }">
          <template v-if="column.key === 'region'"><span class="mono">{{ row.region }}</span></template>
          <template v-else-if="column.key === 'recordCount'">{{ formatCount(row.recordCount) }}</template>
          <template v-else-if="column.key === 'companyCount'">{{ formatCount(row.companyCount) }}</template>
          <template v-else-if="column.key === 'salaryValidCount'">{{ formatCount(row.salaryValidCount) }}</template>
          <template v-else-if="column.key === 'median'">
            {{ row.salary ? `${formatNumber(row.salary.p50)} ${row.salary.unit}` : '薪资不可用' }}
          </template>
          <template v-else-if="column.key === 'quartiles'">
            {{ row.salary ? `${formatNumber(row.salary.p25)} ～ ${formatNumber(row.salary.p75)}` : '—' }}
          </template>
          <template v-else><span class="mono">{{ row.topIndustry ?? '—' }}</span></template>
        </template>
      </DataTable>
    </template>
  </div>
</template>

<style scoped>
.compare__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.compare__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.compare__scale {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  flex: none;
}

.compare__canvas {
  width: 100%;
  height: 220px;
  margin-bottom: var(--space-3);
}
</style>
