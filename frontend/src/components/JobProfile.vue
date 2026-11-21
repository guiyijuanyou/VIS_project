<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JobProfileResponse } from '@/api/types'
import { formatCount, formatNumber, formatPercent } from '@/utils/format'

/**
 * C04：职位画像。三个维度共享同一分母（该职位在当前筛选下的记录数），
 * 占比与样本数并列显示，避免只看到百分比而不知道分母。
 */
const props = defineProps<{ profile: JobProfileResponse }>()

const dimensionLabels: Record<string, string> = {
  industry: '行业（company_type）',
  education: '学历代码',
  experience: '经验代码',
}

const activeDimension = ref<'industry' | 'education' | 'experience'>('industry')

const activeItems = computed(() => props.profile.categories.find((group) => group.dimension === activeDimension.value)?.items ?? [])
const maxShare = computed(() => activeItems.value.reduce((max, item) => Math.max(max, item.share), 0) || 1)
</script>

<template>
  <div class="job-profile">
    <div class="job-profile__summary">
      <div class="job-profile__stat">
        <span class="muted">焦点职位</span>
        <strong class="mono">{{ profile.job }}</strong>
      </div>
      <div class="job-profile__stat">
        <span class="muted">记录数（分母）</span>
        <strong>{{ formatCount(profile.recordCount) }}</strong>
      </div>
      <div class="job-profile__stat">
        <span class="muted">企业数</span>
        <strong>{{ formatCount(profile.companyCount) }}</strong>
      </div>
      <div class="job-profile__stat">
        <span class="muted">覆盖地区数</span>
        <strong>{{ formatCount(profile.regionCount) }}</strong>
      </div>
      <div class="job-profile__stat">
        <span class="muted">有效报价样本</span>
        <strong>{{ formatCount(profile.salaryValidCount) }}</strong>
      </div>
      <div class="job-profile__stat">
        <span class="muted">报价中点 P50 / P25～P75</span>
        <strong>
          {{ profile.salary ? `${formatNumber(profile.salary.p50)} / ${formatNumber(profile.salary.p25)}～${formatNumber(profile.salary.p75)} ${profile.salary.unit}` : '薪资不可用' }}
        </strong>
      </div>
    </div>

    <div class="job-profile__tabs">
      <button
        v-for="(label, key) in dimensionLabels"
        :key="key"
        type="button"
        class="chip"
        :class="{ 'chip--active': activeDimension === key }"
        @click="activeDimension = key as 'industry' | 'education' | 'experience'"
      >
        {{ label }}
      </button>
      <span class="card__hint">分母固定为记录数 {{ formatCount(profile.recordCount) }}；同一类别在悬停时显示原代码。</span>
    </div>

    <ul v-if="activeItems.length" class="job-profile__bars">
      <li v-for="item in activeItems" :key="item.code" class="job-profile__row" :title="`${item.label}：${item.count} 条`">
        <span class="mono job-profile__code">{{ item.label }}</span>
        <div class="job-profile__bar">
          <div class="job-profile__fill" :style="{ width: `${(item.share / maxShare) * 100}%` }"></div>
        </div>
        <span class="job-profile__value">{{ formatPercent(item.share) }}</span>
        <span class="job-profile__count muted">{{ formatCount(item.count) }} 条</span>
      </li>
    </ul>
    <p v-else class="empty-hint">该职位在当前条件下没有类别分布数据。</p>
  </div>
</template>

<style scoped>
.job-profile__summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.job-profile__stat {
  display: flex;
  flex-direction: column;
  background: #fafbfe;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  font-size: 12px;
}

.job-profile__tabs { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }

.job-profile__bars { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }

.job-profile__row { display: grid; grid-template-columns: 84px 1fr 58px 74px; align-items: center; gap: var(--space-2); font-size: 12px; }

.job-profile__code { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.job-profile__bar { height: 10px; background: #eef1f7; border-radius: 5px; overflow: hidden; }

.job-profile__fill { height: 100%; background: var(--color-primary); }

.job-profile__value { text-align: right; font-variant-numeric: tabular-nums; }

.job-profile__count { text-align: right; font-size: 11.5px; }
</style>
