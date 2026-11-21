<script setup lang="ts">
import { computed, ref } from 'vue'
import type { JobDistanceResponse } from '@/api/types'
import { formatNumber, formatPercent } from '@/utils/format'
import DataTable from './DataTable.vue'
import type { DataTableColumn } from './table-types'
import EmptyState from './EmptyState.vue'

/** C04：职位差异矩阵；点击任意一对显示各维贡献，不只报一个总分 */
const props = defineProps<{ data: JobDistanceResponse }>()

const pair = ref<{ a: string; b: string } | null>(null)

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

const columns = computed<DataTableColumn[]>(() => [
  { key: 'job', label: '职位', width: '96px' },
  ...props.data.jobs.map((job) => ({ key: job, label: job, align: 'right' as const, width: '96px' })),
])

const rows = computed(() => props.data.jobs.map((job) => ({ job })))

function cellStyle(value: number | null): Record<string, string> {
  if (value === null) return { color: 'var(--color-text-muted)' }
  return {
    display: 'block',
    width: '100%',
    padding: '4px 8px',
    background: `rgba(41, 76, 105, ${(0.06 + value * 0.72).toFixed(3)})`,
    color: value > 0.5 ? '#ffffff' : 'var(--color-text)',
  }
}

function select(a: string, b: string) {
  if (a === b) return
  pair.value = { a, b }
}

const components = computed(() => (pair.value ? props.data.components[`${pair.value.a}|${pair.value.b}`] ?? null : null))
const pairScore = computed(() => (pair.value ? distance(pair.value.a, pair.value.b) : null))
</script>

<template>
  <div>
    <DataTable :columns="columns" :rows="rows" :row-key="(row) => row.job" dense>
      <template #cell="{ row, column }">
        <template v-if="column.key === 'job'"><span class="mono">{{ row.job }}</span></template>
        <template v-else>
          <button
            class="matrix__cell"
            type="button"
            :style="cellStyle(distance(row.job, column.key))"
            :title="row.job === column.key ? '自身距离为 0' : `查看 ${row.job} 与 ${column.key} 的各维贡献`"
            @click="select(row.job, column.key)"
          >
            {{ distance(row.job, column.key) === null ? '不可比' : formatNumber(distance(row.job, column.key), 3) }}
          </button>
        </template>
      </template>
    </DataTable>

    <p class="chart-note">
      算法：{{ data.algorithmVersion }}；参考集合：{{ data.referenceSet }}。矩阵对称，对角线为 0；任一侧缺少有效报价时该维不参与，单元格显示“不可比”。
    </p>
    <ul class="matrix__warnings">
      <li v-for="warning in data.warnings" :key="warning">{{ warning }}</li>
    </ul>

    <div v-if="pair" class="matrix__detail">
      <h4 class="matrix__detail-title num">
        {{ pair.a }} ↔ {{ pair.b }}：总差异度 {{ pairScore === null ? '不可比' : formatNumber(pairScore, 3) }}
      </h4>
      <ul v-if="components" class="matrix__components">
        <li v-for="component in components" :key="component.dimension" class="matrix__component">
          <span class="matrix__dimension">{{ dimensionLabels[component.dimension] ?? component.dimension }}</span>
          <div class="matrix__bar">
            <div
              class="matrix__fill"
              :style="{ width: component.value === null ? '0%' : `${Math.max(1, component.value * 100)}%` }"
            ></div>
          </div>
          <span class="matrix__value num">
            {{ component.value === null ? '不参与' : formatNumber(component.value, 3) }}
            <span class="text-muted">（{{ formatPercent(component.value) }}）</span>
          </span>
          <span class="matrix__note">{{ component.note }}</span>
        </li>
      </ul>
      <EmptyState v-else title="该对没有返回维度分量" hint="缺少 components，无法解释差异来源。" />
      <p class="chart-note">各维等权平均得到总差异度：这是分析设计，不是事实规律；差异大不代表某职位更好。</p>
    </div>
    <EmptyState v-else title="尚未选择职位对" hint="点击矩阵中任意一对职位，查看各维贡献。" />
  </div>
</template>

<style scoped>
.matrix__cell {
  border: none;
  font-family: inherit;
  font-size: var(--text-xs);
  text-align: right;
  font-variant-numeric: tabular-nums;
  transition: outline-color var(--transition-fast);
}

.matrix__cell:hover {
  outline: 1px solid var(--color-brand);
}

.matrix__warnings {
  margin: var(--space-2) 0 0;
  padding-left: var(--space-4);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.matrix__detail {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: var(--border-width) solid var(--color-border);
}

.matrix__detail-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  margin-bottom: var(--space-3);
}

.matrix__components {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.matrix__component {
  display: grid;
  grid-template-columns: 76px 150px 132px minmax(0, 1fr);
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
}

.matrix__dimension {
  color: var(--color-text);
}

.matrix__bar {
  height: 6px;
  background: var(--color-surface-alt);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.matrix__fill {
  height: 100%;
  background: var(--color-brand);
}

.matrix__value {
  text-align: right;
}

.matrix__note {
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
