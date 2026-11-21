<script setup lang="ts">
import type { DataTableColumn } from './table-types'

/**
 * 数据表：统一表头、行高、数值右对齐与悬停高亮。
 * 单元格内容由 #cell 插槽渲染，列定义决定对齐方式与列宽。
 */
const props = withDefaults(
  defineProps<{ columns: DataTableColumn[]; rows: any[]; rowKey: (row: any) => string; dense?: boolean }>(),
  { dense: false },
)
</script>

<template>
  <div class="dt-wrap scroll-area">
    <table class="dt" :class="{ 'dt--dense': props.dense }">
      <colgroup>
        <col v-for="column in props.columns" :key="column.key" :style="{ width: column.width }" />
      </colgroup>
      <thead>
        <tr>
          <th
            v-for="column in props.columns"
            :key="column.key"
            :class="column.align === 'right' ? 'dt__cell--right' : undefined"
            scope="col"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in props.rows" :key="props.rowKey(row)">
          <td
            v-for="column in props.columns"
            :key="column.key"
            :class="column.align === 'right' ? 'dt__cell--right' : undefined"
          >
            <slot name="cell" :row="row" :column="column">{{ row[column.key] }}</slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.dt-wrap {
  max-width: 100%;
  overflow-x: auto;
}

.dt {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
  /* auto 布局：列宽不足时表格横向滚动，而不是把单元格内容裁掉 */
  table-layout: auto;
}

.dt th,
.dt td {
  padding: 0 var(--space-2);
  height: var(--row-height);
  border-bottom: var(--border-width) solid var(--color-border);
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dt th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--color-surface-alt);
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  border-bottom: var(--border-width) solid var(--color-border-strong);
}

.dt tbody tr:hover td {
  background: var(--color-bg);
}

.dt--dense th,
.dt--dense td {
  height: 28px;
}

.dt__cell--right {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
