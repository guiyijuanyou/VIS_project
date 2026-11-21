<script setup lang="ts">
/** 分页：显示总条数、每页条数与页码；按钮为主+次两级 */
const props = defineProps<{ page: number; pageSize: number; total: number; maxPage: number }>()
const emit = defineEmits<{ (e: 'change', page: number): void }>()

function go(next: number) {
  if (next < 1 || next > props.maxPage || next === props.page) return
  emit('change', next)
}
</script>

<template>
  <div class="pagination">
    <span class="pagination__info num">
      共 {{ props.total.toLocaleString('zh-CN') }} 条 · 每页 {{ props.pageSize }} 条 · 第 {{ props.page }} / {{ props.maxPage }} 页
    </span>
    <div class="pagination__controls">
      <button class="btn" type="button" :disabled="props.page <= 1" @click="go(props.page - 1)">上一页</button>
      <button class="btn" type="button" :disabled="props.page >= props.maxPage" @click="go(props.page + 1)">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding-top: var(--space-3);
  border-top: var(--border-width) solid var(--color-border);
}

.pagination__info {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.pagination__controls {
  display: flex;
  gap: var(--space-2);
}
</style>
