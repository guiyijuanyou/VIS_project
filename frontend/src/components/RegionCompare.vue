<script setup lang="ts">
import { computed, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import type { RegionRow } from '@/api/types'
import { useECharts } from '@/composables/useECharts'
import { AXIS_COLOR, axisStyle } from '@/charts/theme'
import { formatCount, formatNumber } from '@/utils/format'

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
    legend: { top: 0, type: 'scroll' },
    xAxis: { ...axisStyle(), type: 'category', data: industryCodes.value },
    yAxis: {
      ...axisStyle(),
      type: 'value',
      name: '地区内占比',
      axisLabel: { color: AXIS_COLOR, formatter: (value: number) => `${(value * 100).toFixed(0)}%` },
    },
    series: compared.value.map((row) => ({
      name: row.region,
      type: 'bar',
      data: industryCodes.value.map((code) => row.industryShare?.find((item) => item.code === code)?.share ?? 0),
      barMaxWidth: 24,
    })),
  }
}

useECharts(container, option)
</script>

<template>
  <div class="region-compare">
    <p v-if="compared.length === 0" class="empty-hint">在上方散点图中点选 2～4 个地区进行比较。</p>
    <template v-else>
      <div class="region-compare__tags">
        <button v-for="row in compared" :key="row.region" type="button" class="chip chip--active" @click="emit('remove', row.region)">
          {{ row.region }} ✕
        </button>
        <span class="card__hint">分母：各地区在当前筛选条件下的记录数。</span>
      </div>

      <div v-if="hasShare" ref="container" class="region-compare__canvas"></div>
      <p v-else class="empty-hint">接口未返回地区行业占比（industryShare），无法绘制结构比较；需在契约中确认该字段。</p>

      <table class="table">
        <thead>
          <tr>
            <th>地区</th>
            <th>记录数</th>
            <th>企业数</th>
            <th>有效报价样本</th>
            <th>报价中位数</th>
            <th>P25 ～ P75</th>
            <th>占比最高行业</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in compared" :key="row.region">
            <td class="mono">{{ row.region }}</td>
            <td>{{ formatCount(row.recordCount) }}</td>
            <td>{{ formatCount(row.companyCount) }}</td>
            <td>{{ formatCount(row.salaryValidCount) }}</td>
            <td>{{ row.salary ? `${formatNumber(row.salary.p50)} ${row.salary.unit}` : '薪资不可用' }}</td>
            <td>{{ row.salary ? `${formatNumber(row.salary.p25)} ～ ${formatNumber(row.salary.p75)}` : '—' }}</td>
            <td class="mono">{{ row.topIndustry ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<style scoped>
.region-compare__tags { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); }

.region-compare__canvas { width: 100%; height: 240px; }
</style>
