<script setup lang="ts">
import type { SimilarRegionsResponse } from '@/api/types'
import { formatCount, formatPercent } from '@/utils/format'
import Tag from './Tag.vue'

/**
 * C05：相似地区列表。必须写明“基于全局行业发布结构”，避免被理解为地理接近。
 */
defineProps<{ result: SimilarRegionsResponse }>()
const emit = defineEmits<{ (e: 'pick', region: string): void }>()
</script>

<template>
  <div>
    <dl class="similar__meta">
      <div><dt>方法</dt><dd>{{ result.method }}</dd></div>
      <div><dt>比较集合</dt><dd>{{ result.reference }}</dd></div>
    </dl>

    <ul class="similar__list">
      <li v-for="item in result.items" :key="item.region" class="similar__item">
        <Tag tone="neutral" :title="`加入比较：${item.region}`">
          <button class="similar__code mono" type="button" @click="emit('pick', item.region)">{{ item.region }}</button>
        </Tag>
        <div class="similar__bar" :title="`相似度 ${formatPercent(item.similarity)}`">
          <div class="similar__fill" :style="{ width: `${Math.max(2, item.similarity * 100)}%` }"></div>
        </div>
        <span class="similar__value num">{{ formatPercent(item.similarity) }}</span>
        <span class="similar__info num">记录 {{ formatCount(item.recordCount) }} · 主行业 {{ item.topIndustry ?? '—' }}</span>
      </li>
    </ul>

    <p class="chart-note">
      相似度 = 1 − 行业结构总变差距离，范围 0～1；只表示发布结构相近，不代表地理接近，也不含薪资维度。
    </p>
  </div>
</template>

<style scoped>
.similar__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1) var(--space-4);
  margin: 0 0 var(--space-3);
  padding-bottom: var(--space-3);
  border-bottom: var(--border-width) solid var(--color-border);
  font-size: var(--text-xs);
}

.similar__meta div {
  display: flex;
  gap: var(--space-2);
  min-width: 0;
}

.similar__meta dt {
  color: var(--color-text-muted);
  flex: none;
}

.similar__meta dd {
  margin: 0;
  color: var(--color-text-secondary);
}

.similar__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.similar__item {
  display: grid;
  grid-template-columns: 76px minmax(120px, 1fr) 56px 190px;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
}

.similar__code {
  border: none;
  background: transparent;
  padding: 0;
  color: var(--color-brand);
}

.similar__code:hover {
  text-decoration: underline;
}

.similar__bar {
  height: 6px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  overflow: hidden;
}

.similar__fill {
  height: 100%;
  background: var(--color-brand);
}

.similar__value {
  text-align: right;
  color: var(--color-text);
}

.similar__info {
  color: var(--color-text-secondary);
  text-align: right;
}
</style>
