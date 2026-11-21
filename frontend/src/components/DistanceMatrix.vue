<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JobDistanceResponse } from '@/api/types'
import { formatNumber, formatPercent } from '@/utils/format'

/** C04：职位差异矩阵；点击任意一对显示各维贡献，不只报一个总分 */
const props = defineProps<{ data: JobDistanceResponse }>()

const pair = ref<{ a: string; b: string } | null>(null)

const dimensions = computed(() => props.data.dimensions)
const dimensionLabels: Record<string, string> = {
  industry: '行业结构',
  region: '地区结构',
  education: '学历结构',
  experience: '经验结构',
  salary: '报价中位数',
}

function distance(a: string, b: string): number | null {
  const i = props.data.jobs.indexOf(a)
  const j = props.data.jobs.indexOf(b)
  if (i < 0 || j < 0) return null
  return props.data.matrix[i][j]
}

function cellStyle(value: number | null): Record<string, string> {
  if (value === null) return { background: '#f5f6fa', color: '#9aa3b5' }
  const alpha = 0.08 + value * 0.72
  return { background: `rgba(59, 109, 216, ${alpha.toFixed(3)})`, color: value > 0.55 ? '#ffffff' : 'var(--color-text)' }
}

function select(a: string, b: string) {
  if (a === b) return
  pair.value = { a, b }
}

const components = computed(() => {
  if (!pair.value) return null
  return props.data.components[`${pair.value.a}|${pair.value.b}`] ?? null
})

const pairScore = computed(() => (pair.value ? distance(pair.value.a, pair.value.b) : null))
</script>

<template>
  <div class="distance-matrix">
    <table class="table distance-matrix__table">
      <thead>
        <tr>
          <th></th>
          <th v-for="job in data.jobs" :key="job" class="mono">{{ job }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in data.jobs" :key="row">
          <th class="mono">{{ row }}</th>
          <td
            v-for="col in data.jobs"
            :key="col"
            class="distance-matrix__cell"
            :style="cellStyle(distance(row, col))"
            :title="row === col ? '自身距离为 0' : `点击查看 ${row} 与 ${col} 的各维贡献`"
            @click="select(row, col)"
          >
            {{ distance(row, col) === null ? '不可比' : formatNumber(distance(row, col), 3) }}
          </td>
        </tr>
      </tbody>
    </table>

    <p class="card__hint">
      算法：{{ data.algorithmVersion }}；参考集合：{{ data.referenceSet }}。矩阵对称，对角线为 0；任一侧缺少有效报价时该维不参与，单元格显示“不可比”。
    </p>
    <ul class="distance-matrix__warnings">
      <li v-for="warning in data.warnings" :key="warning">{{ warning }}</li>
    </ul>

    <div v-if="pair" class="distance-matrix__detail">
      <h4 class="distance-matrix__detail-title">
        {{ pair.a }} ↔ {{ pair.b }}：总差异度 {{ pairScore === null ? '不可比' : formatNumber(pairScore, 3) }}
      </h4>
      <ul v-if="components" class="distance-matrix__components">
        <li v-for="component in components" :key="component.dimension" class="distance-matrix__component">
          <span class="distance-matrix__dimension">{{ dimensionLabels[component.dimension] ?? component.dimension }}</span>
          <div class="distance-matrix__bar">
            <div
              class="distance-matrix__fill"
              :style="{ width: component.value === null ? '0%' : `${Math.max(1, component.value * 100)}%`, background: component.value === null ? '#c8cedb' : 'var(--color-primary)' }"
            ></div>
          </div>
          <span class="distance-matrix__value">
            {{ component.value === null ? '不参与' : formatNumber(component.value, 3) }}
            <span class="muted">（{{ formatPercent(component.value) }}）</span>
          </span>
          <span class="distance-matrix__note muted">{{ component.note }}</span>
        </li>
      </ul>
      <p v-else class="empty-hint">该对没有返回维度分量（components），无法解释差异来源。</p>
      <p class="card__hint">各维等权平均得到总差异度：这是分析设计，不是事实规律；差异大不代表某职位更好。</p>
    </div>
    <p v-else class="empty-hint">点击矩阵中任意一对职位，查看各维贡献。</p>
  </div>
</template>

<style scoped>
.distance-matrix__table { margin-bottom: var(--space-2); }

.distance-matrix__cell { cursor: pointer; text-align: center; font-variant-numeric: tabular-nums; }

.distance-matrix__warnings { margin: 0 0 var(--space-2); padding-left: 18px; font-size: 11.5px; color: var(--color-text-muted); }

.distance-matrix__detail { border-top: 1px dashed var(--color-border); padding-top: var(--space-3); }

.distance-matrix__detail-title { font-size: 13px; margin-bottom: var(--space-2); }

.distance-matrix__components { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }

.distance-matrix__component { display: grid; grid-template-columns: 76px 160px 120px 1fr; align-items: center; gap: var(--space-2); font-size: 12px; }

.distance-matrix__bar { height: 8px; background: #eef1f7; border-radius: 4px; overflow: hidden; }

.distance-matrix__fill { height: 100%; }

.distance-matrix__value { font-variant-numeric: tabular-nums; }

.distance-matrix__note { font-size: 11px; }
</style>
