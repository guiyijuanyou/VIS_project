<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JobProfileResponse } from '@/api/types'
import { formatCount, formatNumber, formatPercent } from '@/utils/format'
import MetricCard from './MetricCard.vue'
import Tabs from './Tabs.vue'
import Tooltip from './Tooltip.vue'
import EmptyState from './EmptyState.vue'

/**
 * C04：职位画像。三个维度共享同一分母（该职位在当前筛选下的记录数），
 * 占比与样本数并列显示，避免只看到百分比而不知道分母。
 */
const props = defineProps<{ profile: JobProfileResponse }>()

const dimensionItems = [
  { key: 'industry', label: '行业（company_type）' },
  { key: 'education', label: '学历代码' },
  { key: 'experience', label: '经验代码' },
]

const activeDimension = ref<'industry' | 'education' | 'experience'>('industry')

const activeItems = computed(() => props.profile.categories.find((group) => group.dimension === activeDimension.value)?.items ?? [])
const maxShare = computed(() => activeItems.value.reduce((max, item) => Math.max(max, item.share), 0) || 1)

interface MetricDatum {
  label: string
  value: string
  unit?: string
  caption?: string
  tone?: 'default' | 'positive' | 'negative' | 'warning'
}

const stats = computed<MetricDatum[]>(() => {
  const profile = props.profile
  const salary = profile.salary
  return [
    { label: '焦点职位', value: profile.job, caption: 'job_title 代码' },
    { label: '记录数（分母）', value: formatCount(profile.recordCount), caption: '当前条件下该职位记录数' },
    { label: '企业数', value: formatCount(profile.companyCount), caption: '去重企业代码' },
    { label: '覆盖地区数', value: formatCount(profile.regionCount), caption: '去重地区代码' },
    { label: '有效报价样本', value: formatCount(profile.salaryValidCount), caption: 'salary_status = ok' },
    {
      label: '报价中点 P50 / P25～P75',
      value: salary ? `${formatNumber(salary.p50)} / ${formatNumber(salary.p25)}～${formatNumber(salary.p75)}` : '不可用',
      unit: salary ? salary.unit : undefined,
      caption: salary ? `有效样本 ${formatCount(salary.sampleCount)}` : '当前条件无有效报价',
      tone: salary ? 'default' : 'warning',
    },
  ]
})
</script>

<template>
  <div>
    <div class="profile__stats">
      <MetricCard
        v-for="stat in stats"
        :key="stat.label"
        :label="stat.label"
        :value="stat.value"
        :unit="stat.unit"
        :caption="stat.caption"
        :tone="stat.tone"
      />
    </div>

    <div class="profile__controls">
      <Tabs :items="dimensionItems" :model-value="activeDimension" @update:model-value="(value) => (activeDimension = value as 'industry' | 'education' | 'experience')" />
      <span class="profile__scale num">分母：{{ formatCount(profile.recordCount) }} 条记录</span>
    </div>

    <ul v-if="activeItems.length" class="profile__bars">
      <li v-for="item in activeItems" :key="item.code" class="profile__row">
        <Tooltip :text="`原代码 ${item.code} · ${formatCount(item.count)} 条`">
          <span class="profile__code mono">{{ item.label }}</span>
        </Tooltip>
        <div class="profile__bar">
          <div class="profile__fill" :style="{ width: `${(item.share / maxShare) * 100}%` }"></div>
        </div>
        <span class="profile__value num">{{ formatPercent(item.share) }}</span>
        <span class="profile__count num">{{ formatCount(item.count) }} 条</span>
      </li>
    </ul>
    <EmptyState v-else title="没有类别分布数据" hint="该职位在当前条件下没有可用的类别记录。" />
  </div>
</template>

<style scoped>
.profile__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.profile__controls {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.profile__scale {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  padding-bottom: var(--space-2);
}

.profile__bars {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.profile__row {
  display: grid;
  grid-template-columns: 96px minmax(120px, 1fr) 60px 72px;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
}

.profile__row:hover {
  background: var(--color-bg);
}

.profile__code {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-secondary);
}

.profile__bar {
  height: 8px;
  background: var(--color-surface-alt);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.profile__fill {
  height: 100%;
  background: var(--color-brand);
}

.profile__value {
  text-align: right;
  color: var(--color-text);
}

.profile__count {
  text-align: right;
  color: var(--color-text-muted);
}
</style>
