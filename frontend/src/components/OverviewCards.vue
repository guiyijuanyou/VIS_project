<script setup lang="ts">
import type { OverviewResponse } from '@/api/types'
import { formatCount, formatPercent } from '@/utils/format'
import MetricCard from './MetricCard.vue'

/** 总览指标：发布量口径与有效薪资口径分开呈现，单位与统计口径写在次级层 */
const props = defineProps<{ overview: OverviewResponse }>()

interface MetricDatum {
  label: string
  value: string
  unit?: string
  caption?: string
  tone?: 'default' | 'positive' | 'negative' | 'warning'
}

function cards(): MetricDatum[] {
  const overview = props.overview
  return [
    { label: '记录数（发布量）', value: formatCount(overview.recordCount), caption: '样本内招聘记录条数' },
    { label: '企业数', value: formatCount(overview.companyCount), caption: '去重企业代码数' },
    { label: '地区数', value: formatCount(overview.regionCount), caption: '覆盖地区代码数' },
    { label: '职位数', value: formatCount(overview.jobCount), caption: '覆盖职位代码数' },
    {
      label: '有效报价样本',
      value: formatCount(overview.salaryValidCount),
      caption: `占记录数 ${formatPercent(overview.salaryValidRate)}`,
    },
    { label: '有效报价率', value: formatPercent(overview.salaryValidRate), caption: '有效样本 / 记录数' },
    {
      label: '报价中点中位数',
      value: overview.salaryMidMedian === null ? '不可用' : String(overview.salaryMidMedian),
      caption: overview.salaryMidMedian === null ? '当前条件无有效报价' : overview.salaryUnit,
      tone: overview.salaryMidMedian === null ? 'warning' : 'default',
    },
  ]
}
</script>

<template>
  <div class="overview">
    <MetricCard
      v-for="card in cards()"
      :key="card.label"
      :label="card.label"
      :value="card.value"
      :unit="card.unit"
      :caption="card.caption"
      :tone="card.tone"
    />
  </div>
</template>

<style scoped>
.overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
  gap: var(--space-2);
}
</style>
