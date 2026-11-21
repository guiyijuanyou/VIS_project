<script setup lang="ts">
import type { OverviewResponse } from '@/api/types'
import { formatCount, formatPercent } from '@/utils/format'

/** 总览指标：发布量口径与有效薪资口径必须分开显示 */
const props = defineProps<{ overview: OverviewResponse }>()

const cards = [
  { label: '记录数（发布量）', get: () => formatCount(props.overview.recordCount) },
  { label: '企业数', get: () => formatCount(props.overview.companyCount) },
  { label: '地区数', get: () => formatCount(props.overview.regionCount) },
  { label: '职位数', get: () => formatCount(props.overview.jobCount) },
  { label: '有效报价样本', get: () => formatCount(props.overview.salaryValidCount) },
  { label: '有效报价率', get: () => formatPercent(props.overview.salaryValidRate) },
  {
    label: '报价中点中位数',
    get: () =>
      props.overview.salaryMidMedian === null
        ? '薪资不可用'
        : `${props.overview.salaryMidMedian} ${props.overview.salaryUnit}`,
  },
]
</script>

<template>
  <div class="overview-cards">
    <div v-for="card in cards" :key="card.label" class="overview-cards__item">
      <span class="overview-cards__label">{{ card.label }}</span>
      <span class="overview-cards__value">{{ card.get() }}</span>
    </div>
  </div>
</template>

<style scoped>
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--space-2);
}

.overview-cards__item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.overview-cards__label { font-size: 11.5px; color: var(--color-text-muted); }

.overview-cards__value { font-size: 17px; font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
