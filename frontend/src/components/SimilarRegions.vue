<script setup lang="ts">
import type { SimilarRegionsResponse } from '@/api/types'
import { formatCount, formatPercent } from '@/utils/format'

/**
 * C05：相似地区列表。
 * 必须写明“基于全局行业发布结构”，避免被理解为地理接近或发展水平相同。
 */
defineProps<{ result: SimilarRegionsResponse }>()
const emit = defineEmits<{ (e: 'pick', region: string): void }>()
</script>

<template>
  <div class="similar-regions">
    <p class="similar-regions__method">
      方法：{{ result.method }}；比较集合：{{ result.reference }}
    </p>
    <ul class="similar-regions__list">
      <li v-for="item in result.items" :key="item.region" class="similar-regions__item">
        <button type="button" class="similar-regions__code mono" :title="`加入比较：${item.region}`" @click="emit('pick', item.region)">
          {{ item.region }}
        </button>
        <div class="similar-regions__bar">
          <div class="similar-regions__bar-fill" :style="{ width: `${Math.max(2, item.similarity * 100)}%` }"></div>
        </div>
        <span class="similar-regions__value">{{ formatPercent(item.similarity) }}</span>
        <span class="similar-regions__meta muted">
          记录 {{ formatCount(item.recordCount) }} · 主行业 {{ item.topIndustry ?? '—' }}
        </span>
      </li>
    </ul>
    <p class="card__hint">
      相似度 = 1 − 行业结构总变差距离，范围 0～1；只表示发布结构相近，不代表地理接近，也不含薪资维度。
    </p>
  </div>
</template>

<style scoped>
.similar-regions__method { margin: 0 0 var(--space-2); font-size: 12px; color: var(--color-text-muted); }

.similar-regions__list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }

.similar-regions__item { display: grid; grid-template-columns: 72px 1fr 56px 168px; align-items: center; gap: var(--space-2); }

.similar-regions__code { border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-surface); padding: 2px 6px; font-size: 12px; }
.similar-regions__code:hover { border-color: var(--color-primary); color: var(--color-primary); }

.similar-regions__bar { height: 8px; border-radius: 4px; background: #eef1f7; overflow: hidden; }

.similar-regions__bar-fill { height: 100%; background: var(--color-primary); }

.similar-regions__value { font-variant-numeric: tabular-nums; font-size: 12.5px; text-align: right; }

.similar-regions__meta { font-size: 11.5px; }
</style>
